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
        IS_THREEPHASIC = 4

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
        list_a = self.queryset.values_list(
            self.fields[0], self.fields[3]
        )
        list_b = self.queryset.values_list(
            self.fields[1], self.fields[3]
        )
        list_c = self.queryset.values_list(
            self.fields[2], self.fields[3]
        )

        minutely_measurements = {}
        minutely_measurements['transductor'] = transductor
        minutely_measurements['phase_a'] = list_a
        minutely_measurements['phase_b'] = list_b
        minutely_measurements['phase_c'] = list_c

        return [minutely_measurements]

    def simple_measurement_collections(self, transductor):
        list_measurement = self.queryset.values_list(
            self.fields[0], self.fields[1]
        )

        minutely_measurements = {}
        minutely_measurements['transductor'] = transductor
        minutely_measurements['measurement'] = list_measurement

        return [minutely_measurements]


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
    fields = [
        'active_power_a',
        'active_power_b',
        'active_power_c',
        'collection_time'
    ]


class MinutelyReactivePowerThreePhaseViewSet(MinutelyMeasurementViewSet):
    serializer_class = ThreePhaseSerializer
    fields = [
        'reactive_power_a',
        'reactive_power_b',
        'reactive_power_c',
        'collection_time'
    ]


class MinutelyApparentPowerThreePhaseViewSet(MinutelyMeasurementViewSet):
    """
    A ViewSet class responsible to get the minutely apparent power
    three phase

    Attributes:

        MinutelyMeasurementViewSet:  a ViewSet class responsible for the
        minutely measurement
    """
    serializer_class = ThreePhaseSerializer
    fields = [
        'apparent_power_a',
        'apparent_power_b',
        'apparent_power_c',
        'collection_time'
    ]


class MinutelyPowerFactorThreePhaseViewSet(MinutelyMeasurementViewSet):
    serializer_class = ThreePhaseSerializer
    fields = [
        'power_factor_a',
        'power_factor_b',
        'power_factor_c',
        'collection_time'
    ]


class MinutelyDHTVoltageThreePhaseViewSet(MinutelyMeasurementViewSet):
    serializer_class = ThreePhaseSerializer
    fields = [
        'dht_voltage_a',
        'dht_voltage_b',
        'dht_voltage_c',
        'collection_time'
    ]


class MinutelyDHTCurrentThreePhaseViewSet(MinutelyMeasurementViewSet):
    serializer_class = ThreePhaseSerializer
    fields = [
        'dht_current_a',
        'dht_current_b',
        'dht_current_c',
        'collection_time'
    ]


class MinutelyTotalActivePowerViewSet(MinutelyMeasurementViewSet):
    serializer_class = MeasurementSerializer
    fields = ['total_active_power', 'collection_time']


class MinutelyTotalReactivePowerViewSet(MinutelyMeasurementViewSet):
    serializer_class = MeasurementSerializer
    fields = ['total_reactive_power', 'collection_time']


class MinutelyTotalApparentPowerViewSet(MinutelyMeasurementViewSet):
    serializer_class = MeasurementSerializer
    fields = ['total_apparent_power', 'collection_time']


class MinutelyTotalPowerFactorViewSet(MinutelyMeasurementViewSet):
    serializer_class = MeasurementSerializer
    fields = ['total_power_factor', 'collection_time']


class VoltageThreePhaseViewSet(MinutelyMeasurementViewSet):
    serializer_class = ThreePhaseSerializer
    fields = ['voltage_a', 'voltage_b', 'voltage_c', 'collection_time']


class CurrentThreePhaseViewSet(MinutelyMeasurementViewSet):
    serializer_class = ThreePhaseSerializer
    fields = ['current_a', 'current_b', 'current_c', 'collection_time']


class FrequencyViewSet(MinutelyMeasurementViewSet):
    serializer_class = MeasurementSerializer
    fields = ['frequency_a', 'collection_time']
