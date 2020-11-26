from django.utils import timezone
import numpy as np
import re
import os
import csv
import codecs
from .lttb import downsample

from django.db.models.query import QuerySet

from rest_framework import serializers
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import permissions

from rest_framework.response import Response

from rest_framework.exceptions import APIException
from rest_framework.exceptions import NotAcceptable

from rest_framework.decorators import api_view

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
from .serializers import TaxSerializer

from django.http import StreamingHttpResponse
from django.utils.translation import ugettext as _


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

        transductor_id = self.request.query_params.get('id')

        if transductor_id:
            params['id'] = transductor_id
        transductor = None

        MeasurementParamsValidator.validate_query_params(params)

        try:
            transductor = EnergyTransductor.objects.get(
                id=transductor_id
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
    fields = ['generated_energy_peak_time', 'generated_energy_off_peak_time']
    information = 'generation'

    def list(self, request):
        self.filter_queryset_by_date()
        self.filter_queryset_by_campus()
        self.filter_queryset_by_group()
        self.filter_queryset_by_transductor()

        return Response(
            self.mount_data_list(), 
            status=200
        )

    def filter_queryset_by_date(self):
        date_params = self.get_date_params()
        self.validate_date_params(date_params)

        self.queryset = self.queryset.filter(
            collection_date__range=(
                date_params['start_date'], 
                date_params['end_date']
            )
        )

    def get_date_params(self):
        date_params = {}

        start_date = self.request.query_params.get('start_date')
        if start_date:
            date_params['start_date'] = start_date
        
        end_date = self.request.query_params.get('end_date')
        if end_date:
            date_params['end_date'] = end_date
        else:
            end_date = timezone.now()
            end_date = end_date.strftime("%Y-%m-%d %H:%M:%S")
            date_params['end_date'] = str(end_date)

        return date_params


    def validate_date_params(self, date_params):
        try:
            MeasurementParamsValidator.validate_query_params(
                date_params, ignore=['id']
            )
        except APIException as exception:
            fields = exception.get_full_details()
            if 'start_date' not in fields or 'end_date' not in fields:
                raise exception

    def filter_queryset_by_campus(self):
        campus = self.request.query_params.get('campus')

        # Filter queryset by campus only if campus is in query_params
        if campus:
            try:
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

    def filter_queryset_by_group(self):
        group = self.request.query_params.get('group')

        # Filter queryset by group only if group is in query_params
        if group:
            try:
                group = Group.objects.get(
                        pk=int(group)
                    )
                self.queryset = self.queryset.filter(
                    transductor__grouping__in=[group]
                )
            except Group.DoesNotExist:
                raise APIException(
                    'Group id does not match with '
                    'any existent group.'
                )

    def filter_queryset_by_transductor(self):
        transductor_id = self.request.query_params.get('id')
        
        # Filter queryset by transductor only if transductor id is in query_params
        if transductor_id:
            try:
                transductor = EnergyTransductor.objects.get(
                    pk=int(transductor_id)
                )
                self.queryset = self.queryset.filter(
                    transductor=transductor
                )
            except EnergyTransductor.DoesNotExist:
                raise APIException(
                    'Transductor id does not match with '
                    'any existent energy transductor'
                )

    def mount_data_list(self, transductor=[]):
        data = {}
        data[self.information] = []
        data['min'] = 0
        data['max'] = 0

        measurements = self.queryset.order_by('collection_date').values(
            self.fields[0], self.fields[1], 'collection_date'
        )
        
        if measurements:
            response = self.apply_algorithm(measurements)
            for value in response:
                total = (value[1] + value[2])

                if total > data['max']:
                    data['max'] = total

                data[self.information].append([value[0], total])

        return data

    def apply_algorithm(self, measurements, transductor=[]):
        periodicity = self.request.query_params.get('type')

        measurements_list = (
            [
                [
                    measurements[0]['collection_date'],
                    0,
                    0
                ]
            ]
        )

        if periodicity == 'hourly':
            self.get_hourly_measurements(measurements, measurements_list)
        elif periodicity == 'daily':
            self.get_daily_measurements(measurements, measurements_list)
        else:
            measurements_list = []

        return measurements_list

    def get_hourly_measurements(self, measurements, measurements_list):
        for i in range(0, len(measurements)):
            actual = measurements[i]['collection_date']
            last = measurements_list[len(measurements_list) - 1][0]

            last_hour = (last.hour)

            if actual.hour == last_hour:
                self.build_data(
                    actual, measurements, measurements_list, i
                )
            else:
                self.finish_data(
                    actual, last, measurements, measurements_list, i
                )

            last = measurements_list[len(measurements_list) - 1][0]
            measurements_list[len(measurements_list) - 1][0] = (
                timezone.datetime(
                    last.year, last.month, last.day,
                    last.hour, 0, 0
                ).strftime('%m/%d/%Y %H:%M:%S')
            )

    def get_daily_measurements(self, measurements, measurements_list):
        for i in range(0, len(measurements) - 1):
            actual = measurements[i]['collection_date']
            last = measurements_list[len(measurements_list) - 1][0]

            last_day = (last.day)

            if actual.day == last_day:
                self.build_data(
                    actual, measurements, measurements_list, i
                )
            else:
                last.hour = 0
                self.finish_data(
                    actual, last, measurements, measurements_list, i
                )
            
            last = measurements_list[len(measurements_list) - 1][0]
            measurements_list[len(measurements_list) - 1][0] = (
                timezone.datetime(
                    last.year, last.month, last.day,
                    0, 0, 0
                ).strftime('%m/%d/%Y %H:%M:%S')
            )

    def build_data(
        self, actual, measurements, measurements_list, index
    ):
        measurements_list[len(measurements_list) - 1][0] = (
            measurements[index]['collection_date']
        )
        measurements_list[len(measurements_list) - 1][1] += \
            measurements[index][self.fields[1]]

    def finish_data(self, actual, last, measurements, measurements_list, index):
        answer_date = timezone.datetime(
            actual.year, actual.month,
            actual.day, actual.hour, 0, 0
        )

        measurements_list[len(measurements_list) - 1][0] = (
            timezone.datetime(
                last.year, last.month, last.day,
                last.hour, 0, 0
            ).strftime('%m/%d/%Y %H:%M:%S')
        )

        measurements_list.append(
            [
                answer_date,
                measurements[index][self.fields[1]],
                0
            ]
        )


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


class TotalConsumptionViewSet(QuarterlyMeasurementViewSet):
    serializer_class = QuarterlySerializer
    fields = ['consumption_peak_time', 'consumption_off_peak_time']
    information = 'consumption'


class TotalGenerationViewSet(QuarterlyMeasurementViewSet):
    serializer_class = QuarterlySerializer
    fields = ['generated_energy_peak_time', 'generated_energy_off_peak_time']
    information = 'generation'


class TotalInductivePowerViewSet(QuarterlyMeasurementViewSet):
    serializer_class = QuarterlySerializer
    fields = ['inductive_power_peak_time', 'inductive_power_off_peak_time']
    information = 'inductive_power'


class TotalCapacitivePowerViewSet(QuarterlyMeasurementViewSet):
    serializer_class = QuarterlySerializer
    fields = ['capacitive_power_peak_time', 'capacitive_power_off_peak_time']
    information = 'capacitive_power'


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

        measurements = self.queryset.order_by('collection_date').values(
            self.fields[0], self.fields[1], 'collection_date',
            'tax__value_peak', 'tax__value_off_peak'
        )
        
        if measurements:
            response = self.apply_algorithm(
                measurements
            )

            for value in response:
                total_cost = (value[1] + value[2]) / 1000

                if total_cost > data['max']:
                    data['max'] = total_cost

                data['cost'].append([value[0], total_cost])

        return data

    def apply_algorithm(self, measurements, transductor=[]):
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
            for i in range(0, len(measurements)):
                actual = measurements[i]['collection_date']

                last_day = (
                    measurements_list[len(measurements_list) - 1][0].day
                )

                if actual.day == last_day:
                    self.build_data(
                        actual, measurements, measurements_list, i
                    )
                else:
                    self.finish_data(
                        actual, measurements, measurements_list, i, type
                    )

            last = measurements_list[len(measurements_list) - 1][0]
            measurements_list[len(measurements_list) - 1][0] = (
                timezone.datetime(
                    last.year, last.month, last.day,
                    0, 0, 0
                ).strftime('%m/%d/%Y %H:%M:%S')
            )
        elif type == 'monthly':
            for i in range(0, len(measurements) - 1):
                actual = measurements[i]['collection_date']

                last_month = (
                    measurements_list[len(measurements_list) - 1][0].month
                )

                if actual.month == last_month:
                    self.build_data(
                        actual, measurements, measurements_list, i
                    )
                else:
                    self.finish_data(
                        actual, measurements, measurements_list, i, type
                    )

            last = measurements_list[-1][0]
            measurements_list[-1][0] = (
                timezone.datetime(
                    last.year, last.month, 1,
                    0, 0, 0
                ).strftime('%m/%d/%Y %H:%M:%S')
            )
        elif type == 'yearly':
            for i in range(0, len(measurements)):
                actual = measurements[i]['collection_date']

                last_year = (
                    measurements_list[-1][0].year
                )

                if actual.year == last_year:
                    self.build_data(
                        actual, measurements, measurements_list, i
                    )
                else:
                    self.finish_data(
                        actual, measurements, measurements_list, i, type
                    )

            last = measurements_list[-1][0]
            measurements_list[-1][0] = (
                timezone.datetime(
                    last.year, 1, 1,
                    0, 0, 0
                ).strftime('%m/%d/%Y %H:%M:%S')
            )
        else:
            measurements_list = []

        return measurements_list

    def build_data(
            self, actual, measurements, measurements_list, index
    ):
        measurements_list[-1][0] = (
            measurements[index]['collection_date']
        )
        if actual.hour in range(0, 17) \
           or actual.hour in range(21, 23):
            value_off_peak = measurements[index]['tax__value_off_peak']
            measurements_list[-1][1] += \
                measurements[index][self.fields[1]] \
                * value_off_peak if value_off_peak else 1
        else:
            value_peak = measurements[index]['tax__value_peak']
            measurements_list[-1][2] += \
                measurements[index][self.fields[0]] \
                * value_peak if value_peak else 1

    def finish_data(
            self, actual, measurements, measurements_list, index, type
    ):
        answer_date = timezone.datetime(
            actual.year, actual.month,
            actual.day, actual.hour, 0, 0
        )

        last = measurements_list[len(measurements_list) - 1][0]

        if type == 'daily':
            measurements_list[-1][0] = (
                timezone.datetime(
                    last.year, last.month, last.day,
                    0, 0, 0
                ).strftime('%m/%d/%Y %H:%M:%S')
            )
        elif type == 'monthly':
            measurements_list[-1][0] = (
                timezone.datetime(
                    last.year, last.month, 1,
                    0, 0, 0
                ).strftime('%m/%d/%Y %H:%M:%S')
            )
        elif type == 'yearly':
            measurements_list[-1][0] = (
                timezone.datetime(
                    last.year, 1, 1,
                    0, 0, 0
                ).strftime('%m/%d/%Y %H:%M:%S')
            )

        if actual.hour in range(0, 17) \
           or actual.hour in range(21, 23):
            value_off_peak = measurements[index]['tax__value_off_peak']
            measurements_list.append(
                [
                    answer_date,
                    measurements[index][self.fields[1]] * (
                        value_off_peak if value_off_peak else 1
                    ),
                    0
                ]
            )
        else:
            value_peak = measurements[index]['tax__value_peak']
            measurements_list.append(
                [
                    answer_date,
                    0,
                    measurements[index][self.fields[0]] * (
                        value_peak if value_peak else 1
                    )
                ]
            )


class RealTimeMeasurementViewSet(MeasurementViewSet):
    serializer_class = RealTimeMeasurementSerializer

    def get_queryset(self):
        transductor_id = self.request.query_params.get('id')
        if transductor_id:
            try:
                transductor = EnergyTransductor.objects.get(
                    id=transductor_id)
                queryset = RealTimeMeasurement.objects.filter(
                    transductor=transductor)
            except Exception:
                exception = APIException(
                    transductor_id,
                    _('This id does not match with any Transductor'),
                )
                exception.status_code = 400
                raise exception
        else:
            queryset = RealTimeMeasurement.objects.select_related(
                'transductor'
            ).all()

        return queryset


class Echo:
    def write(self, value):
        return value


class MeasurementResults(mixins.RetrieveModelMixin,
                         mixins.ListModelMixin,
                         viewsets.GenericViewSet):
    @api_view(['GET'])
    def mount_csv_measurement(request):
        class_name = request.query_params.get('class_name')
        fields = request.query_params.get('fields')
        start_date = request.query_params.get('start_date')

        queryset = None

        if class_name == 'minutely':
            queryset = MeasurementResults.build_csv(
                request, MinutelyMeasurement, fields, start_date
            )
        elif class_name == 'quarterly':
            queryset = MeasurementResults.build_csv(
                request, QuarterlyMeasurement, fields, start_date
            )
        elif class_name == 'monthly':
            queryset = MeasurementResults.build_csv(
                request, MonthlyMeasurement, fields, start_date
            )

        if queryset:
            pseudo_buffer = Echo()
            pseudo_buffer.write(codecs.BOM_UTF8)

            writer = csv.writer(pseudo_buffer)
            response = StreamingHttpResponse(
                (writer.writerow(measurement) for measurement in queryset),
                content_type='text/csv'
            )
            response['Content-Disposition'] = (
                'attachment; filename="measurement_dataset.csv"'
            )
            response['Content-Transfer-Encoding'] = 'binary'

            return response
        else:
            exception = APIException(
                'Class name was not specified in request params.'
            )
            exception.status_code = 400
            raise exception

    @staticmethod
    def build_csv(request, class_name, fields, start_date):
        all_fields = {
            measurement.name: measurement.verbose_name
            for measurement in class_name._meta.get_fields()
        }

        if start_date is None:
            raise NotAcceptable(
                'Start date param is needed to create the csv file.'
            )

        if fields is not None:
            columns = fields.split(',')
        else:
            columns = []

        queryset = list(
            class_name.objects.filter(
                collection_date__gte=start_date
            ).values_list(*columns)
        )

        if columns:
            queryset.insert(
                0,
                [
                    all_fields[column] for column in columns
                    if column in all_fields
                ]
            )
        else:
            queryset.insert(
                0,
                [
                    measurement.verbose_name
                    for measurement in class_name._meta.get_fields()
                ]
            )

        return queryset


class TaxViewSet(viewsets.ModelViewSet):
    queryset = Tax.objects.all()
    serializer_class = TaxSerializer
    permission_classes = (permissions.AllowAny,)
