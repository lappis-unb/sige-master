from rest_framework import serializers, viewsets, mixins

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

    def get_queryset(self):
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        serial_number = self.request.query_params.get('serial_number', None)

        if serial_number is not None:
            try:
                transductor = EnergyTransductor.objects.get(
                    serial_number=serial_number
                )
            except EnergyTransductor.DoesNotExist:
                return []

        if((start_date is not None) and (end_date is not None)):
            self.queryset = self.queryset.filter(
                collection_date__gte=start_date
            )
            self.queryset = self.queryset.filter(collection_date__lte=end_date)

        return self.queryset.reverse()


class MinutelyMeasurementViewSet(MeasurementViewSet):
    collect = MinutelyMeasurement.objects.select_related('transductor').all()
    queryset = collect.order_by('id')
    serializer_class = MinutelyMeasurementSerializer
    pagination_class = PostLimitOffsetPagination


class QuarterlyMeasurementViewSet(MeasurementViewSet):
    collect = QuarterlyMeasurement.objects.select_related('transductor').all()
    queryset = collect.order_by('id')
    serializer_class = QuarterlyMeasurementSerializer
    pagination_class = PostLimitOffsetPagination


class MonthlyMeasurementViewSet(MeasurementViewSet):
    collect = MonthlyMeasurement.objects.select_related('transductor').all()
    queryset = collect.order_by('id')
    serializer_class = MonthlyMeasurementSerializer
    pagination_class = PostLimitOffsetPagination


class VoltageThreePhaseViewSet(MinutelyMeasurementViewSet):
    serializer_class = VoltageThreePhaseSerializer


class CurrentThreePhaseViewSet(MinutelyMeasurementViewSet):
    serializer_class = CurrentThreePhaseSerializer
