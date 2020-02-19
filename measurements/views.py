from django.utils import timezone
import numpy as np
import os
from .lttb import downsample

from django.db.models.query import QuerySet

from rest_framework import serializers
from rest_framework import viewsets
from rest_framework import mixins

from rest_framework.exceptions import APIException

from transductors.models import EnergyTransductor

from measurements.utils import MeasurementParamsValidator

from .models import Measurement
from .models import MinutelyMeasurement
from .models import QuarterlyMeasurement
from .models import MonthlyMeasurement
from .models import RealTimeMeasurement
from .models import EnergyTransductor

from .serializers import MeasurementSerializer
from .serializers import ThreePhaseSerializer
from .serializers import MinutelyMeasurementSerializer
from .serializers import QuarterlyMeasurementSerializer
from .serializers import MonthlyMeasurementSerializer
from .serializers import QuarterlySerializer
from .serializers import RealTimeMeasurementSerializer


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


class QuarterlyMeasurementViewSet(MeasurementViewSet):
    model = QuarterlyMeasurement
    queryset = QuarterlyMeasurement.objects.none()
    serializer_class = QuarterlyMeasurementSerializer

    # def get_queryset(self):
    #     start_date = self.request.query_params.get('start_date')
    #     end_date = self.request.query_params.get('end_date')

    #     params = [
    #         {'name': 'start_date', 'value': start_date},
    #         {'name': 'end_date', 'value': end_date}
    #     ]

    #     validations.validate_query_params(params)

    #     try:
    #         self.queryset = self.model.objects.filter(
    #             collection_date__gte=start_date,
    #             collection_date__lte=end_date
    #         ).order_by(
    #             'collection_date'
    #         )
    #     except EnergyTransductor.DoesNotExist:
    #         raise APIException(
    #             'Serial number field does not match '
    #             'any existent EnergyTransductor.'
    #         )

    #     return self.mount_data_list()

    def mount_data_list(self, transductor=[]):
        total_consumption_per_hour = []

        for field in self.fields:
            measurements = self.queryset.values(
                field, 'collection_date'
            )

            if measurements:
                total_consumption_per_hour = self.apply_algorithm(
                    measurements,
                    field
                )

        return total_consumption_per_hour

    def apply_algorithm(self, measurements, field, transductor=[]):
        measurements_list = (
            [
                [
                    measurements[0]['collection_date'],
                    measurements[0][field],
                ]
            ]
        )

        for i in range(1, len(measurements) - 1):
            actual = measurements[i]['collection_date']
            last = measurements[i - 1]['collection_date']

            if actual.minute < 15:
                answer_hour = actual.hour
            else:
                answer_hour = actual.hour + 1

            last_hour = measurements_list[len(measurements_list) - 1][0].hour

            if answer_hour == last_hour:
                measurements_list[len(measurements_list) - 1][1] += (
                    measurements[i][field]
                )
            else:
                answer_date = timezone.datetime(
                    actual.year, actual.month,
                    actual.day, answer_hour, 0, 0
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

        quarterly_measurements = {}
        quarterly_measurements['measurements'] = measurements_list

        if transductor != []:
            quarterly_measurements['transductor'] = transductor

        return [quarterly_measurements]


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
