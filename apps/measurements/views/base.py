import logging

from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action

from apps.measurements.filters import (
    CumulativeMeasurementFilter,
    InstantMeasurementFilter,
)
from apps.measurements.models import CumulativeMeasurement, InstantMeasurement
from apps.measurements.pagination import MeasurementPagination
from apps.measurements.serializers import (
    CumulativeMeasurementQuerySerializer,
    CumulativeMeasurementSerializer,
    InstantMeasurementQuerySerializer,
    InstantMeasurementSerializer,
)
from apps.measurements.services.csv_generator import generate_csv_response

logger = logging.getLogger("apps.measurements.views.base")


class InstantMeasurementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InstantMeasurement.objects.all()
    serializer_class = InstantMeasurementSerializer
    filterset_class = InstantMeasurementFilter
    pagination_class = MeasurementPagination

    @extend_schema(parameters=[InstantMeasurementQuerySerializer])
    @action(detail=False, methods=["get"], url_path="export-csv")
    def export_csv(self, request):
        validated_params = self._validate_params(request, raise_exception=True)
        fields = validated_params.get("fields")
        queryset = self.filter_queryset(self.get_queryset())
        return generate_csv_response(queryset, fields=fields, filename="instant_measurements.csv")

    def _validate_params(self, request, raise_exception=True):
        params_serializer = InstantMeasurementQuerySerializer(data=request.query_params)
        params_serializer.is_valid(raise_exception=raise_exception)
        return params_serializer.validated_data


class CumulativeMeasurementViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CumulativeMeasurementSerializer
    queryset = CumulativeMeasurement.objects.all()
    filterset_class = CumulativeMeasurementFilter
    pagination_class = MeasurementPagination

    @action(detail=False, methods=["get"], url_path="export-csv")
    def export_csv(self, request):
        validated_params = self._validate_params(request, raise_exception=True)
        queryset = self.filter_queryset(self.get_queryset())
        fields = validated_params.get("fields")
        return generate_csv_response(queryset, fields=fields, filename="cumulative_measurements.csv")

    def _validate_params(self, request, raise_exception=True):
        params_serializer = CumulativeMeasurementQuerySerializer(data=request.query_params)
        params_serializer.is_valid(raise_exception=raise_exception)
        return params_serializer.validated_data
