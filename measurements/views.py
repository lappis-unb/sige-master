from rest_framework import serializers, viewsets, mixins
from rest_framework.exceptions import APIException
from django.db.models.query import QuerySet
from .utils import *

from transductors.models import EnergyTransductor

from .models import Measurement
from .models import MinutelyMeasurement
from .models import QuarterlyMeasurement
from .models import MonthlyMeasurement

from .serializers import MeasurementSerializer
from .serializers import ThreePhaseSerializer
from .serializers import MinutelyMeasurementSerializer
from .serializers import QuarterlyMeasurementSerializer
from .serializers import MonthlyMeasurementSerializer

from .lttb import downsample
import numpy as np
from datetime import datetime
#  this viewset don't inherits from viewsets.ModelViewSet because it
#  can't have update and create methods so it only inherits from parts of it
from .models import EnergyTransductor

from .pagination import PostLimitOffsetPagination
from .pagination import PostPageNumberPagination


class MeasurementViewSet(mixins.RetrieveModelMixin,
                         mixins.DestroyModelMixin,
                         mixins.ListModelMixin,
                         viewsets.GenericViewSet):
    queryset = None
    model = None
    pagination_class = PostLimitOffsetPagination
    fields = []

    def get_queryset(self):
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        serial_number = self.request.query_params.get('serial_number')
        transductor = None

        params = [
            {'name': 'start_date', 'value': start_date},
            {'name': 'end_date', 'value': end_date},
            {'name': 'serial_number', 'value': serial_number}
        ]

        validate_query_params(params)

        try:
            transductor = EnergyTransductor.objects.get(
                serial_number=serial_number
            )
            self.queryset = self.model.objects.filter(
                transductor=transductor,
                collection_time__gte=start_date,
                collection_time__lte=end_date
            ).order_by(
                'collection_time'
            )
        except EnergyTransductor.DoesNotExist:
            raise APIException(
                'Serial number field does not match '
                'any existent EnergyTransductor.'
            )

        return self.mount_data_list(transductor)

    def mount_data_list(self, transductor):
        return []


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
        list_a = self.apply_filter(self.fields[0])
        list_b = self.apply_filter(self.fields[1])
        list_c = self.apply_filter(self.fields[2])

        minutely_measurements = {}
        minutely_measurements['transductor'] = transductor
        minutely_measurements['phase_a'] = list_a
        minutely_measurements['phase_b'] = list_b
        minutely_measurements['phase_c'] = list_c

        return [minutely_measurements]

    def simple_measurement_collections(self, transductor):
        list_measurement = self.apply_filter(self.fields[0])

        minutely_measurements = {}
        minutely_measurements['transductor'] = transductor
        minutely_measurements['measurement'] = list_measurement

        return [minutely_measurements]


    def apply_filter(self, value):
        filtered_values = self.queryset.values(
            value, 'collection_time'
        )
        indexes = range(len(filtered_values))
        filtered_values = (
            [
                [
                    counter,
                    item[value],
                    datetime.timestamp(item['collection_time'])
                ]
                for counter, item in zip(indexes, filtered_values)
            ]
        )
        filtered_values = np.array(filtered_values)
        filtered_values = downsample(filtered_values, 10)
        filtered_values = (
            [
                [
                    item[1],
                    datetime
                        .utcfromtimestamp(item[2])
                        .strftime('%d/%m/%Y %H:%M:%S')
                ]
                for item in filtered_values
            ]
        )

        return filtered_values


class QuarterlyMeasurementViewSet(MeasurementViewSet):
    model = QuarterlyMeasurement
    queryset = QuarterlyMeasurement.objects.none()
    serializer_class = QuarterlyMeasurementSerializer


class MonthlyMeasurementViewSet(MeasurementViewSet):
    model = MonthlyMeasurement
    queryset = MonthlyMeasurement.objects.none()
    serializer_class = MonthlyMeasurementSerializer


class MinutelyActivePowerThreePhaseViewSet(MinutelyMeasurementViewSet):
    serializer_class = ThreePhaseSerializer
    fields = ['active_power_a', 'active_power_b', 'active_power_c']


class MinutelyReactivePowerThreePhaseViewSet(MinutelyMeasurementViewSet):
    serializer_class = ThreePhaseSerializer
    fields = ['reactive_power_a', 'reactive_power_b', 'reactive_power_c']


class MinutelyApparentPowerThreePhaseViewSet(MinutelyMeasurementViewSet):
    """
    A ViewSet class responsible to get the minutely apparent power
    three phase

    Attributes:

        MinutelyMeasurementViewSet:  a ViewSet class responsible for the
        minutely measurement
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
