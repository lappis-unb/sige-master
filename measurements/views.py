from rest_framework import serializers, viewsets, mixins
from rest_framework.exceptions import APIException
from django.db.models.query import QuerySet
from .exceptions import *
from .utils import *

from .models import Measurement
from .models import MinutelyMeasurement
from .models import QuarterlyMeasurement
from .models import MonthlyMeasurement
from .models import EnergyTransductor

from .serializers import *

from .pagination import PostLimitOffsetPagination
from .pagination import PostPageNumberPagination


class MeasurementViewSet(mixins.RetrieveModelMixin,
                         mixins.DestroyModelMixin,
                         mixins.ListModelMixin,
                         viewsets.GenericViewSet):
    queryset = None
    model = None
    pagination_class = PostLimitOffsetPagination

    def get_queryset(self):
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        serial_number = self.request.query_params.get('serial_number')
        transductor = None

        try:
            params = [
                {'name': 'start_date', 'value': start_date},
                {'name': 'end_date', 'value': end_date},
                {'name': 'serial_number', 'value': serial_number}
            ]

            validate_query_params(params)
        except MeasurementsParamsException as exception:
            raise exception

        try:
            transductor = EnergyTransductor.objects.get(
                serial_number=serial_number
            )
            self.queryset = self.model.objects.filter(
                collection_time__gte=start_date
            )
            self.queryset = self.queryset.filter(collection_time__lte=end_date)
        except EnergyTransductor.DoesNotExist:
            raise APIException(
                'Serial number field not match '
                'with any EnergyTransductor existent.'
            )

        return self.mount_data_list(transductor)

    def mount_data_list(self):
        pass


class MinutelyMeasurementViewSet(MeasurementViewSet):
    model = MinutelyMeasurement
    queryset = MinutelyMeasurement.objects.none()
    serializer_class = MinutelyMeasurementSerializer


class QuarterlyMeasurementViewSet(MeasurementViewSet):
    model = QuarterlyMeasurement
    queryset = QuarterlyMeasurement.objects.none()
    serializer_class = QuarterlyMeasurementSerializer


class MonthlyMeasurementViewSet(MeasurementViewSet):
    model = MonthlyMeasurement
    queryset = MonthlyMeasurement.objects.none()
    serializer_class = MonthlyMeasurementSerializer


class VoltageThreePhaseViewSet(MinutelyMeasurementViewSet):
    serializer_class = VoltageThreePhaseSerializer


class CurrentThreePhaseViewSet(MinutelyMeasurementViewSet):
    serializer_class = CurrentThreePhaseSerializer

    def mount_data_list(self, transductor):
        list_current_a = \
            [data.__dict__['current_a'] for data in self.queryset]
        list_current_b = \
            [data.__dict__['current_b'] for data in self.queryset]
        list_current_c = \
            [data.__dict__['current_c'] for data in self.queryset]
        list_collection_time = \
            [data.__dict__['collection_time'] for data in self.queryset]

        minutely_measurements = {}
        minutely_measurements['transductor'] = transductor
        minutely_measurements['collections_time'] = list_collection_time
        minutely_measurements['list_current_a'] = list_current_a
        minutely_measurements['list_current_b'] = list_current_b
        minutely_measurements['list_current_c'] = list_current_c

        return [minutely_measurements]


class FrequencyViewSet(MinutelyMeasurementViewSet):
    serializer_class = FrequencySerializer
