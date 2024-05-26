import logging

from django.db.models import Case, Count, Max, Min, Q, Sum, When
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
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
    ReportQuerySerializer,
    ReportSerializer,
    UferQuerySerializer,
    UferSerializer,
)
from apps.organizations.models import Entity
from apps.transductors.models import Transductor

logger = logging.getLogger("apps.measurements.views.report")


@extend_schema(parameters=[ReportQuerySerializer])
class ReportViewSet(ListModelMixin, GenericViewSet):
    queryset = CumulativeMeasurement.objects.all()
    serializer_class = ReportSerializer
    filterset_class = CumulativeMeasurementFilter

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset()
        validated_params = getattr(self, "validated_params", None)
        try:
            fields = validated_params.get("fields", [])
            queryset = queryset.values("collection_date", *fields)
        except Exception as e:
            raise ValidationError({"error": str(e)})
        filterset = self.filterset_class(self.validated_params, queryset=queryset)
        return filterset.qs

    def list(self, request, *args, **kwargs):
        self.validated_params = self._validate_params(request, raise_exception=True)
        fields = self.validated_params.get("fields")
        entity_id = self.validated_params.get("entity")
        include_descendants = self.validated_params.get("inc_desc")

        queryset = self.get_queryset()
        transductors = Transductor.objects.entity(entity_id, include_descendants)
        measurements_qs = queryset.filter(transductor__in=transductors)
        aggregated_qs = self._aggregate_data(measurements_qs, fields)

        serializer = self.get_serializer(data=aggregated_qs, context={"fields": fields})
        serializer.is_valid(raise_exception=True)

        if not serializer.data:
            return Response({"detail": "No data found."}, status=status.HTTP_204_NO_CONTENT)

        response_data = self._build_response_data(aggregated_qs, serializer.data, transductors)
        return Response(response_data, status=status.HTTP_200_OK)

    def _aggregate_data(self, queryset, fields):
        aggregates = {field: Sum(field) for field in fields}
        aggregates["total_measurements"] = Count("id")
        aggregates["start_date"] = Min("collection_date")
        aggregates["end_date"] = Max("collection_date")
        return queryset.aggregate(**aggregates)

    def _validate_params(self, request, raise_exception=True):
        params_serializer = ReportQuerySerializer(data=request.query_params)
        params_serializer.is_valid(raise_exception=raise_exception)
        return params_serializer.validated_data

    def _build_response_data(self, aggregated_qs, data, transductors):
        entity = Entity.objects.get(pk=self.validated_params.get("entity"))
        transductors_ip = sorted(transductors.values_list("ip_address", flat=True))
        list_descendants = [f"{desc.acronym} - {desc.name}" for desc in entity.get_descendants()]

        return {
            "Organization": f"{entity.acronym} - {entity.name}",
            "Descendants": list_descendants,
            "period": {
                "start": aggregated_qs["start_date"],
                "end": aggregated_qs["end_date"],
            },
            "transductors": transductors_ip,
            "total_measurements": aggregated_qs["total_measurements"],
            "results": data,
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
                .exclude(power_factor_a=0, power_factor_b=0, power_factor_c=0)
                .values(*fields, "collection_date", "transductor")
            )
        except Exception as e:
            raise ValidationError({"error": str(e)})

        filterset = self.filterset_class(self.validated_params, queryset=queryset)
        return filterset.qs

    def list(self, request, *args, **kwargs):
        self.validated_params = self._validate_params(request, raise_exception=True)
        fields = self.validated_params.get("fields")
        entity_id = self.validated_params.get("entity")
        include_descendants = self.validated_params.get("inc_desc")
        threshold_percent = self.validated_params.get("th_percent")

        queryset = self.get_queryset()
        transductors = Transductor.objects.entity(entity_id, include_descendants)
        measurements_qs = queryset.filter(transductor__in=transductors)

        aggregated_qs = self._aggregate_data(measurements_qs, fields, threshold_percent)
        processed_data = [self.calculate_percent(data, fields) for data in aggregated_qs]
        serializer = self.get_serializer(data=processed_data, many=True, context={"fields": fields})
        serializer.is_valid(raise_exception=True)

        if not serializer.data:
            return Response({"detail": "No data found."}, status=status.HTTP_204_NO_CONTENT)

        response_data = self._build_response_data(aggregated_qs, serializer.data, transductors, threshold_percent)
        return Response(response_data, status=status.HTTP_200_OK)

    def _aggregate_data(self, queryset, fields, threshold):
        filter_conditions = self._get_filter_conditions(fields, threshold)
        annotations = self._get_annotations(fields, filter_conditions)
        return queryset.values("transductor").annotate(**annotations).order_by("transductor")

    def _get_filter_conditions(self, fields, threshold):
        th_decimal = threshold / 100
        conditions = Q()
        for field in fields:
            conditions |= Q(**{f"{field}__gte": th_decimal}) | Q(**{f"{field}__lte": -th_decimal})
        return conditions

    def _get_annotations(self, fields, filter_conditions):
        annotations = {
            "start_date": Min("collection_date"),
            "end_date": Max("collection_date"),
            "total_measurements": Count("id"),
        }
        for field in fields:
            annotations[f"{field}_len_total"] = Count(field)
            annotations[f"{field}_len_quality"] = Count(Case(When(filter_conditions, then=1)))
        return annotations

    def calculate_percent(self, transductor_data, fields):
        data = transductor_data.copy()
        for field in fields:
            len_total = data[f"{field}_len_total"]
            len_quality = data[f"{field}_len_quality"]
            quality_rate = len_quality / len_total if len_total else 0.0
            data[f"pf_phase_{field[-1]}"] = round(quality_rate * 100, 2)
        return data

    def _validate_params(self, request, raise_exception=True):
        params_serializer = UferQuerySerializer(data=request.query_params)
        params_serializer.is_valid(raise_exception=raise_exception)
        return params_serializer.validated_data

    def _build_response_data(self, aggregated_qs, data, transductors, threshold):
        entity = Entity.objects.filter(pk=self.validated_params.get("entity")).values("acronym", "name").first()
        total_measurements = sum(data["total_measurements"] for data in aggregated_qs)

        return {
            "Organization": f"{entity['acronym']} - {entity['name']}",
            "period": {
                "start_date": aggregated_qs[0].get("start_date"),
                "end_date": aggregated_qs[0].get("end_date"),
            },
            "total_measurements": total_measurements,
            "info": f"Results in (%) above the threshold {threshold}%.",
            "results": data,
        }
