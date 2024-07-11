import logging

from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.measurements.filters import (
    CumulativeMeasurementFilter,
    InstantMeasurementFilter,
)
from apps.measurements.models import CumulativeMeasurement, InstantMeasurement
from apps.measurements.serializers import (
    ReportDetailSerializer,
    ReportQuerySerializer,
    ReportSummarySerializer,
    UferQuerySerializer,
    UferSerializer,
)
from apps.measurements.services import ReportDataAggregator, UferDataAggregator
from apps.organizations.models import Entity
from apps.transductors.models import Transductor

logger = logging.getLogger("apps.measurements.views.report")


@extend_schema(parameters=[ReportQuerySerializer])
class ReportViewSet(ListModelMixin, GenericViewSet):
    queryset = CumulativeMeasurement.objects.all()
    serializer_class = ReportSummarySerializer
    filterset_class = CumulativeMeasurementFilter

    def get_queryset(self, *args, **kwargs):
        # queryset = super().get_queryset()
        validated_params = getattr(self, "validated_params", None)
        try:
            fields = validated_params.get("fields", [])
            queryset = super().get_queryset().values(*fields, "collection_date", "transductor")

        except Exception as e:
            raise ValidationError({"error": str(e)})

        filterset = self.filterset_class(self.validated_params, queryset=queryset)
        return filterset.qs

    def list(self, request, *args, **kwargs):
        self.validated_params = self._validate_params(request, raise_exception=True)
        fields = self.validated_params.get("fields")
        detail = self.validated_params.get("detail")

        root_entity = self._get_entity()
        transductors_entity = Transductor.objects.entity(
            entity=root_entity,
            inc_desc=self.validated_params.get("inc_desc"),
            depth=self.validated_params.get("max_depth"),
        )

        queryset = self._get_filtered_queryset(transductors_entity)
        if not queryset:
            return Response({"detail": "No data found."}, status=status.HTTP_204_NO_CONTENT)

        response_data = self._aggregate_data(queryset, fields, detail)
        agg_fields = self._get_agg_fields(fields)

        if detail:
            serializer = ReportDetailSerializer(data=list(response_data), many=True, context={"fields": agg_fields})
        else:
            serializer = ReportSummarySerializer(data=response_data, context={"fields": agg_fields})

        serializer.is_valid(raise_exception=True)

        response_data = self._build_response_data(queryset, serializer.data, root_entity)
        return Response(response_data, status=status.HTTP_200_OK)

    def _get_entity(self):
        entity_id = self.validated_params.get("entity")

        try:
            return Entity.objects.get(pk=entity_id)
        except Entity.DoesNotExist:
            raise ValidationError({"error": f"Entity with id {entity_id} not found"})

    def _get_filtered_queryset(self, transductors):
        transductor = self.validated_params.get("transductor")

        if transductor is None:
            return self.get_queryset().filter(transductor__in=transductors)
        elif transductors.filter(pk=transductor).exists():
            return self.get_queryset().filter(transductor=transductor)
        else:
            raise ValidationError({"error": f"Transductor id:{transductor} not found in the entity or descendants"})

    def _get_agg_fields(self, fields):
        agg_fields = []
        for field in fields:
            agg_fields.extend([f"{field}_peak", f"{field}_off_peak"])
        return agg_fields

    def _aggregate_data(self, queryset, fields, detail):
        aggregator = ReportDataAggregator()
        return aggregator.perform_aggregation(queryset, fields, detail)

    def _validate_params(self, request, raise_exception=True):
        params_serializer = ReportQuerySerializer(data=request.query_params)
        params_serializer.is_valid(raise_exception=raise_exception)
        return params_serializer.validated_data

    def _build_response_data(self, queryset, data, entity):
        return {
            "Entity": f"{entity.acronym} - {entity.name}",
            "total_measurements": queryset.count(),
            "tariff_peak": settings.TARIFF_PEAK,
            "tariff_off_peak": settings.TARIFF_OFF_PEAK,
            "results": data,
            "info": "Results in kWh",
        }


@extend_schema(parameters=[UferQuerySerializer])
class UferViewSet(ListModelMixin, GenericViewSet):
    queryset = InstantMeasurement.objects.all()
    serializer_class = UferSerializer
    filterset_class = InstantMeasurementFilter

    def get_queryset(self, *args, **kwargs):
        validated_params = getattr(self, "validated_params", None)
        try:
            fields = validated_params.get("fields", [])
            queryset = (
                super()
                .get_queryset()
                # .exclude(power_factor_a=0, power_factor_b=0, power_factor_c=0)
                .values(*fields, "collection_date", "transductor")
            )
        except Exception as e:
            raise ValidationError({"error": str(e)})

        filterset = self.filterset_class(self.validated_params, queryset=queryset)
        return filterset.qs

    def list(self, request, *args, **kwargs):
        self.validated_params = self._validate_params(request, raise_exception=True)
        fields = self.validated_params.get("fields")
        threshold_percent = self.validated_params.get("th_percent")

        root_entity = self._get_entity()
        transductors_entity = Transductor.objects.entity(
            entity=root_entity,
            inc_desc=self.validated_params.get("inc_desc"),
            depth=self.validated_params.get("max_depth"),
        )

        queryset = self._get_filtered_queryset(transductors_entity)
        if not queryset:
            return Response({"detail": "No data found."}, status=status.HTTP_204_NO_CONTENT)

        response_data = self._aggregate_data(queryset, fields, threshold_percent)
        serializer = self.get_serializer(data=response_data, many=True, context={"fields": fields})
        serializer.is_valid(raise_exception=True)

        response_data = self._build_response_data(queryset, serializer.data, root_entity, threshold_percent)
        return Response(response_data, status=status.HTTP_200_OK)

    def _get_entity(self):
        entity_id = self.validated_params.get("entity")
        try:
            return Entity.objects.get(pk=entity_id)
        except Entity.DoesNotExist:
            raise ValidationError({"error": f"Entity with id {entity_id} not found"})

    def _get_filtered_queryset(self, transductors):
        transductor = self.validated_params.get("transductor")

        if transductor is None:
            return self.get_queryset().filter(transductor__in=transductors)
        if transductors.filter(pk=transductor).exists():
            return self.get_queryset().filter(transductor=transductor)
        else:
            raise ValidationError({"error": f"Transductor id: {transductor} not found in the Entity or Descendants"})

    def _aggregate_data(self, queryset, fields, threshold):
        aggregator = UferDataAggregator()
        aggregated_data = aggregator.perform_aggregation(queryset, fields, threshold)

        return [self.process_data(data, fields) for data in aggregated_data]

    def process_data(self, transductor_data, fields):
        data = transductor_data.copy()
        for field in fields:
            len_total = data[f"{field}_len_total"]
            len_quality = data[f"{field}_len_quality"]
            quality_rate = len_quality / len_total if len_total else 0.0
            data[f"pf_phase_{field[-1]}"] = round(quality_rate * 120, 2)
        return data

    def _validate_params(self, request, raise_exception=True):
        params_serializer = UferQuerySerializer(data=request.query_params)
        params_serializer.is_valid(raise_exception=raise_exception)
        return params_serializer.validated_data

    def _build_response_data(self, queryset, data, entity, threshold):
        return {
            "Entity": f"{entity.acronym} - {entity.name}",
            "total_measurements": queryset.count(),
            "info": f"Results in (%) above the threshold {threshold}%.",
            "results": data,
        }
