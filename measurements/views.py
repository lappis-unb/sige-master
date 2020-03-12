from django.utils import timezone
import numpy as np
import os
import re
from .lttb import downsample

from django.db.models.query import QuerySet

from rest_framework import serializers
from rest_framework import viewsets
from rest_framework import mixins

from rest_framework.response import Response

from rest_framework.exceptions import APIException

from transductors.models import EnergyTransductor

from campi.models import Campus

from groups.models import Group

from measurements.utils import MeasurementParamsValidator

from .models import Measurement
from .models import MinutelyMeasurement
from .models import QuarterlyMeasurement
from .models import MonthlyMeasurement
from .models import RealTimeMeasurement
from .models import EnergyTransductor
from .models import Tax

from .serializers import MeasurementSerializer
from .serializers import ThreePhaseSerializer
from .serializers import MinutelyMeasurementSerializer
from .serializers import QuarterlyMeasurementSerializer
from .serializers import MonthlyMeasurementSerializer
from .serializers import QuarterlySerializer
from .serializers import RealTimeMeasurementSerializer

from django.utils.translation import gettext_lazy as _


#  this viewset don't inherits from viewsets.ModelViewSet because it
#  can't have update and create methods so it only inherits from parts of it
class MeasurementViewSet(mixins.RetrieveModelMixin,
                         mixins.DestroyModelMixin,
                         mixins.ListModelMixin,
                         viewsets.GenericViewSet):
    queryset = None
    model = None
    fields = []

    def get_queryset(self):
        params = {}
        start_date = self.request.query_params.get('start_date')
        if start_date:
            params['start_date'] = start_date
        end_date = self.request.query_params.get('end_date')
        if end_date:
            params['end_date'] = end_date
        else:
            end_date = timezone.now()
            end_date = end_date.strftime("%Y-%m-%d %H:%M:%S")
            params['end_date'] = str(end_date)

        serial_number = self.request.query_params.get('serial_number')
        if serial_number:
            params['serial_number'] = serial_number
        transductor = None

        MeasurementParamsValidator.validate_query_params(params)

        try:
            transductor = EnergyTransductor.objects.get(
                serial_number=serial_number
            )
            self.queryset = self.model.objects.filter(
                transductor=transductor,
                collection_date__gte=start_date,
                collection_date__lte=end_date
            ).order_by(
                'collection_date'
            )
        except EnergyTransductor.DoesNotExist:
            raise APIException(
                'Serial number field does not match '
                'any existent EnergyTransductor.'
            )

        return self.mount_data_list(transductor)


class MinutelyMeasurementViewSet(MeasurementViewSet):
    model = MinutelyMeasurement
    queryset = MinutelyMeasurement.objects.none()
    serializer_class = MinutelyMeasurementSerializer
    fields = []

    def mount_data_list(self, transductor):
        minutely_measurements = []
        IS_THREEPHASIC = 3

        if len(self.fields) is IS_THREEPHASIC:
            minutely_measurements = self.threephasic_measurement_collections(
                transductor
            )
        else:
            minutely_measurements = self.simple_measurement_collections(
                transductor
            )

        return minutely_measurements

    def threephasic_measurement_collections(self, transductor):
        is_filtered = self.request.query_params.get('is_filtered')

        if is_filtered == 'True':
            list_a = self.apply_filter(self.fields[0])
            list_b = self.apply_filter(self.fields[1])
            list_c = self.apply_filter(self.fields[2])
        else:
            list_a = self.queryset.values_list(
                self.fields[0], 'collection_date'
            )
            list_a = (
                [
                    [element[1].strftime('%m/%d/%Y %H:%M:%S'), element[0]]
                    for element in list_a
                ]
            )
            list_b = self.queryset.values_list(
                self.fields[1], 'collection_date'
            )
            list_b = (
                [
                    [element[1].strftime('%m/%d/%Y %H:%M:%S'), element[0]]
                    for element in list_b
                ]
            )
            list_c = self.queryset.values_list(
                self.fields[2], 'collection_date'
            )
            list_c = (
                [
                    [element[1].strftime('%m/%d/%Y %H:%M:%S'), element[0]]
                    for element in list_c
                ]
            )

        minutely_measurements = {}
        minutely_measurements['transductor'] = transductor
        minutely_measurements['phase_a'] = list_a
        minutely_measurements['phase_b'] = list_b
        minutely_measurements['phase_c'] = list_c

        return [minutely_measurements]

    def simple_measurement_collections(self, transductor):
        is_filtered = self.request.query_params.get('is_filtered')

        if is_filtered == 'True':
            list_measurement = self.apply_filter(self.fields[0])
        else:
            list_measurement = self.queryset.values_list(
                self.fields[0], 'collection_date'
            )

        minutely_measurements = {}
        minutely_measurements['transductor'] = transductor
        minutely_measurements['measurements'] = list_measurement

        return [minutely_measurements]

    def apply_filter(self, value):
        filtered_values = self.queryset.values(
            value, 'collection_date'
        )
        indexes = range(len(filtered_values))
        filtered_values = (
            [
                [
                    counter,
                    item[value],
                    timezone.datetime.timestamp(item['collection_date'])
                ]
                for counter, item in zip(indexes, filtered_values)
            ]
        )
        filtered_values = np.array(filtered_values)
        filtered_values = downsample(
            filtered_values,
            int(os.getenv('LIMIT_FILTER'))
        )
        filtered_values = (
            [
                [
                    timezone.datetime
                    .utcfromtimestamp(item[2])
                    .strftime('%m/%d/%Y %H:%M:%S'),
                    item[1]
                ]
                for item in filtered_values
            ]
        )

        return filtered_values


class QuarterlyMeasurementViewSet(mixins.RetrieveModelMixin,
                                  mixins.DestroyModelMixin,
                                  mixins.ListModelMixin,
                                  viewsets.GenericViewSet):
    model = QuarterlyMeasurement
    queryset = QuarterlyMeasurement.objects.all()
    serializer_class = QuarterlyMeasurementSerializer
    fields = []

    def list(self, request):
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        campus = self.request.query_params.get('campus')
        group = self.request.query_params.get('group')
        serial_number = self.request.query_params.get('serial_number')

        try:
            if start_date is not None and end_date is not None:
                self.queryset = self.model.objects.filter(
                    collection_date__range=(start_date, end_date)
                ).order_by(
                    'collection_date'
                )

            if group:
                group = Group.objects.get(
                    pk=int(group)
                )
                self.queryset = self.model.objects.filter(
                    transductor__grouping__in=[group]
                )

            if serial_number:
                transductor = EnergyTransductor.objects.get(
                    pk=int(serial_number)
                )
                self.queryset = self.model.objects.filter(
                    transductor=transductor
                )

            if campus:
                campus = Campus.objects.get(
                    pk=int(campus)
                )
                self.queryset = self.queryset.filter(
                    transductor__campus__in=[campus]
                )
        except Campus.DoesNotExist:
            raise APIException(
                'Campus id does not match with '
                'any existent campus.'
            )
        except Group.DoesNotExist:
            raise APIException(
                'Group id does not match with '
                'any existent group.'
            )

        return Response(self.mount_data_list(), status=200)

    def mount_data_list(self, transductor=[]):
        response = []

        for field in self.fields:
            measurements = self.queryset.values(
                field, 'collection_date'
            )

            if measurements:
                response = self.apply_algorithm(
                    measurements,
                    field
                )

        return response

    def apply_algorithm(self, measurements, field, transductor=[]):
        measurements_list = (
            [
                [
                    measurements[0]['collection_date'],
                    measurements[0][field]
                ]
            ]
        )

        for i in range(1, len(measurements) - 1):
            actual = measurements[i]['collection_date']

            last_hour = measurements_list[len(measurements_list) - 1][0].hour

            if actual.hour == last_hour:
                measurements_list[len(measurements_list) - 1][1] += (
                    measurements[i][field]
                )
            else:
                answer_date = timezone.datetime(
                    actual.year, actual.month,
                    actual.day, actual.hour, 0, 0
                )
                measurements_list[len(measurements_list) - 1][0] = (
                    measurements_list[len(measurements_list) - 1][0]
                    .strftime('%m/%d/%Y %H:%M:%S')
                )
                measurements_list.append(
                    [
                        answer_date,
                        measurements[i][field],
                    ]
                )

        measurements_list[len(measurements_list) - 1][0] = (
            measurements_list[len(measurements_list) - 1][0]
            .strftime('%m/%d/%Y %H:%M:%S')
        )

        return measurements_list


class MonthlyMeasurementViewSet(MeasurementViewSet):
    model = MonthlyMeasurement
    queryset = MonthlyMeasurement.objects.none()
    serializer_class = MonthlyMeasurementSerializer


class MinutelyActivePowerThreePhaseViewSet(MinutelyMeasurementViewSet):
    serializer_class = ThreePhaseSerializer
    fields = ['active_power_a', 'active_power_b', 'active_power_c']


class MinutelyReactivePowerThreePhaseViewSet(MinutelyMeasurementViewSet):
    """
    A ViewSet Class responsible to get reactive power measurements.

    Attributes:
        model(MinutelyMeasurement): The model which save measurements per
        minute of transductores.
        serializer_class(ThreePhaseSerializer): The serialiazer that
        convert model's information to serializer format of rest framework.
        fields(reactive_power_a, reactive_power_b, reactive_power_c): fields
        representing all measurements that is referenced by this ViewSet.

        Example of use:
            >> queryset = MinutelyMeasurement.objects.all()
            >> serializer_class = ThreePhaseSerializer
    """
    serializer_class = ThreePhaseSerializer
    fields = ['reactive_power_a', 'reactive_power_b', 'reactive_power_c']


class MinutelyApparentPowerThreePhaseViewSet(MinutelyMeasurementViewSet):
    """
    A ViewSet class responsible to get the minutely apparent power
    three phase.

    Attributes:
        model(MinutelyMeasurement): The model which save measurements per
        minute of transductores.
        serializer_class(ThreePhaseSerializer): The serialiazer that
        convert model's information to serializer format of rest framework.
        fields(apparent_power_a, apparent_power_b, apparent_power_c): fields
        representing all measurements that is referenced by this ViewSet.

        Example of use:
            >> queryset = MinutelyMeasurement.objects.all()
            >> serializer_class = ThreePhaseSerializer

    """
    serializer_class = ThreePhaseSerializer
    fields = ['apparent_power_a', 'apparent_power_b', 'apparent_power_c']


class MinutelyPowerFactorThreePhaseViewSet(MinutelyMeasurementViewSet):
    serializer_class = ThreePhaseSerializer
    fields = ['power_factor_a', 'power_factor_b', 'power_factor_c']


class MinutelyDHTVoltageThreePhaseViewSet(MinutelyMeasurementViewSet):
    serializer_class = ThreePhaseSerializer
    fields = ['dht_voltage_a', 'dht_voltage_b', 'dht_voltage_c']


class MinutelyDHTCurrentThreePhaseViewSet(MinutelyMeasurementViewSet):
    serializer_class = ThreePhaseSerializer
    fields = ['dht_current_a', 'dht_current_b', 'dht_current_c']


class MinutelyTotalActivePowerViewSet(MinutelyMeasurementViewSet):
    serializer_class = MeasurementSerializer
    fields = ['total_active_power']


class MinutelyTotalReactivePowerViewSet(MinutelyMeasurementViewSet):
    serializer_class = MeasurementSerializer
    fields = ['total_reactive_power']


class MinutelyTotalApparentPowerViewSet(MinutelyMeasurementViewSet):
    serializer_class = MeasurementSerializer
    fields = ['total_apparent_power']


class MinutelyTotalPowerFactorViewSet(MinutelyMeasurementViewSet):
    serializer_class = MeasurementSerializer
    fields = ['total_power_factor']


class VoltageThreePhaseViewSet(MinutelyMeasurementViewSet):
    serializer_class = ThreePhaseSerializer
    fields = ['voltage_a', 'voltage_b', 'voltage_c']


class CurrentThreePhaseViewSet(MinutelyMeasurementViewSet):
    serializer_class = ThreePhaseSerializer
    fields = ['current_a', 'current_b', 'current_c']


class FrequencyViewSet(MinutelyMeasurementViewSet):
    serializer_class = MeasurementSerializer
    fields = ['frequency_a']


class ConsumptionPeakViewSet(QuarterlyMeasurementViewSet):
    serializer_class = QuarterlySerializer
    fields = ['consumption_peak_time']


class ConsumptionOffPeakViewSet(QuarterlyMeasurementViewSet):
    serializer_class = QuarterlySerializer
    fields = ['consumption_off_peak_time']


class GenerationPeakViewSet(QuarterlyMeasurementViewSet):
    serializer_class = QuarterlySerializer
    fields = ['generated_energy_peak_time']


class GenerationOffPeakViewSet(QuarterlyMeasurementViewSet):
    serializer_class = QuarterlySerializer
    fields = ['generated_energy_off_peak_time']


class TotalConsumtionViewSet(QuarterlyMeasurementViewSet):
    serializer_class = QuarterlySerializer
    fields = ['consumption_peak_time', 'consumption_off_peak_time']


class TotalGenerationViewSet(QuarterlyMeasurementViewSet):
    serializer_class = QuarterlySerializer
    fields = ['generated_energy_peak_time', 'generated_energy_off_peak_time']


class DailyConsumptionViewSet(QuarterlyMeasurementViewSet):
    serializer_class = QuarterlySerializer
    fields = ['consumption_peak_time', 'consumption_off_peak_time']

    def mount_data_list(self, transductor=[]):
        total_consumption_per_hour = []
        response = [0] * 24

        for field in self.fields:
            measurements = self.queryset.values(
                field, 'collection_date'
            )

            if measurements:
                total_consumption_per_hour = self.apply_algorithm(
                    measurements,
                    field
                )
                for measurement in total_consumption_per_hour:
                    position = int(
                        re.search('([ ][0-9]+)', measurement[0]).group(0)
                    )
                    response[position] = measurement[1]

        return response


class CostConsumptionViewSet(QuarterlyMeasurementViewSet):
    serializer_class = QuarterlySerializer
    fields = ['consumption_peak_time', 'consumption_off_peak_time']

    def mount_data_list(self, transductor=[]):
        data = {}
        data['cost'] = []
        data['min'] = 0
        data['max'] = 0

        for field in self.fields:
            measurements = self.queryset.order_by('collection_date').values(
                field, 'collection_date',
                'tax__value_peak', 'tax__value_off_peak'
            )

            if measurements:
                response = self.apply_algorithm(
                    measurements,
                    field
                )

                for value in response:
                    total_cost = value[1] + value[2]

                    if total_cost > data['max']:
                        data['max'] = total_cost

                    data['cost'].append([value[0], total_cost])

        return data

    def apply_algorithm(self, measurements, field, transductor=[]):
        type = self.request.query_params.get('type')

        measurements_list = (
            [
                [
                    measurements[0]['collection_date'],
                    0,
                    0
                ]
            ]
        )

        if type == 'daily':
            for i in range(0, len(measurements) - 1):
                actual = measurements[i]['collection_date']

                last_day = (
                    measurements_list[len(measurements_list) - 1][0].day
                )

                if actual.day == last_day:
                    self.build_data(
                        actual, measurements, measurements_list, field, i
                    )
                else:
                    self.finish_data(
                        actual, measurements, measurements_list, field, i
                    )

            measurements_list[len(measurements_list) - 1][0] = (
                measurements_list[len(measurements_list) - 1][0]
                .strftime('%m/%d/%Y %H:%M:%S')
            )
        elif type == 'monthly':
            for i in range(0, len(measurements) - 1):
                actual = measurements[i]['collection_date']

                last_month = (
                    measurements_list[len(measurements_list) - 1][0].month
                )

                if actual.month == last_month:
                    self.build_data(
                        actual, measurements, measurements_list, field, i
                    )
                else:
                    self.finish_data(
                        actual, measurements, measurements_list, field, i
                    )

            measurements_list[len(measurements_list) - 1][0] = (
                measurements_list[len(measurements_list) - 1][0]
                .strftime('%m/%d/%Y %H:%M:%S')
            )

        return measurements_list

    def build_data(
            self, actual, measurements, measurements_list, field, index
    ):
        measurements_list[len(measurements_list) - 1][0] = (
            measurements[index]['collection_date']
        )
        if actual.hour in range(0, 17) \
           or actual.hour in range(21, 23):
            measurements_list[len(measurements_list) - 1][1] += \
                measurements[index][field] \
                * measurements[index]['tax__value_off_peak']
        else:
            measurements_list[len(measurements_list) - 1][2] += \
                measurements[index][field] \
                * measurements[index]['tax__value_peak']

    def finish_data(
            self, actual, measurements, measurements_list, field, index
    ):
        answer_date = timezone.datetime(
            actual.year, actual.month,
            actual.day, actual.hour, 0, 0
        )
        measurements_list[len(measurements_list) - 1][0] = (
            measurements_list[len(measurements_list) - 1][0]
            .strftime('%m/%d/%Y %H:%M:%S')
        )

        if actual.hour in range(0, 17) \
           or actual.hour in range(21, 23):
            value_off_peak = measurements[index]['tax__value_off_peak']
            measurements_list.append(
                [
                    answer_date,
                    measurements[index][field] * value_off_peak,
                    0
                ]
            )
        else:
            value_peak = measurements[index]['tax__value_peak']
            measurements_list.append(
                [
                    answer_date,
                    0,
                    measurements[index][field] * value_peak
                ]
            )


class RealTimeMeasurementViewSet(MeasurementViewSet):
    serializer_class = RealTimeMeasurementSerializer

    def get_queryset(self):
        serial_number = self.request.query_params.get('serial_number')
        if serial_number:
            try:
                transductor = EnergyTransductor.objects.get(
                    serial_number=serial_number)
                queryset = RealTimeMeasurement.objects.filter(
                    transductor=transductor)
            except Exception:
                exception = APIException(
                    serial_number,
                    _('This serial_number does not match with any Transductor'),
                )
                exception.status_code = 400
                raise exception
        else:
            queryset = RealTimeMeasurement.objects.all()
        return queryset
