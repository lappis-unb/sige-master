import logging

import pandas as pd
from django.db.models import Case, Count, Max, Min, Q, Sum, When
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.measurements.filters import (
    CumulativeMeasurementFilter,
    InstantMeasurementFilter,
)
from apps.measurements.models import CumulativeMeasurement, InstantMeasurement
from apps.measurements.pagination import MeasurementPagination
from apps.measurements.serializers import (
    CumulativeGraphQuerySerializer,
    CumulativeMeasurementQuerySerializer,
    CumulativeMeasurementSerializer,
    DetailDailySerializer,
    GraphDataSerializer,
    InstantGraphQuerySerializer,
    InstantMeasurementQuerySerializer,
    InstantMeasurementSerializer,
    ReportQuerySerializer,
    ReportSerializer,
    UferQuerySerializer,
    UferSerializer,
)
from apps.measurements.services.csv_generator import generate_csv_response
from apps.measurements.services.downsampler import LTTBDownSampler
from apps.organizations.models import Entity
from apps.transductors.models import Transductor

logger = logging.getLogger("apps.measurements.views")


class InstantMeasurementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InstantMeasurement.objects.all()
    serializer_class = InstantMeasurementSerializer
    filterset_class = InstantMeasurementFilter
    pagination_class = MeasurementPagination

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


class InstantGraphViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InstantMeasurement.objects.all()
    serializer_class = GraphDataSerializer
    filterset_class = InstantMeasurementFilter

    def list(self, request, *args, **kwargs):
        self.validated_params = self._validate_params(request, raise_exception=True)
        lttb = self.validated_params["lttb"]
        threshold = self.validated_params["threshold"]

        queryset = self.get_queryset()
        if not queryset:
            return Response({"detail": "No data found."}, status=status.HTTP_204_NO_CONTENT)

        data = pd.DataFrame(list(queryset))
        response = self._apply_lttb(data, threshold) if lttb else data
        serializer = self.get_serializer(response)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_queryset(self, *args, **kwargs):
        validated_params = getattr(self, "validated_params", None)
        try:
            fields = validated_params.get("fields", [])
            queryset = super().get_queryset().values("collection_date", *fields)
        except Exception as e:
            raise ValidationError({"error": str(e)})
        filterset = self.filterset_class(self.validated_params, queryset=queryset)
        return filterset.qs

    def _apply_lttb(self, df, threshold):
        try:
            downsampler = LTTBDownSampler(threshold, enable_parallel=True)
            return downsampler.apply_lttb(df, dt_column="collection_date")
        except Exception as e:
            logger.error(f"Error in apply_lttb: {e}")
            raise ValidationError({"error": str(e)})

    def _validate_params(self, request, raise_exception=True):
        params_serializer = InstantGraphQuerySerializer(data=request.query_params)
        params_serializer.is_valid(raise_exception=raise_exception)
        return params_serializer.validated_data


class CumulativeGraphViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CumulativeMeasurement.objects.all()
    serializer_class = GraphDataSerializer
    filterset_class = CumulativeMeasurementFilter

    def list(self, request, *args, **kwargs):
        self.validated_params = self._validate_params(request, raise_exception=True)

        queryset = self.get_queryset()
        if not queryset:
            return Response({"detail": "No data found."}, status=status.HTTP_204_NO_CONTENT)

        data = pd.DataFrame(list(queryset))
        response = self.apply_resample(data) if self.validated_params.get("freq") else data
        serializer = self.get_serializer(response)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_queryset(self, *args, **kwargs):
        validated_params = getattr(self, "validated_params", None)

        try:
            fields = validated_params.get("fields", [])
            queryset = super().get_queryset().values("collection_date", *fields)
        except Exception as e:
            raise ValidationError({"error": str(e)})

        filterset = self.filterset_class(self.validated_params, queryset=queryset)
        return filterset.qs

    def apply_resample(self, df, dropna=True):
        freq = self.validated_params.get("freq")
        agg_func = self.validated_params.get("agg")
        if freq is None or agg_func is None:
            return df

        df_resampled = df.resample(freq, on="collection_date").apply(agg_func)
        df_resampled = df_resampled.reset_index()
        df_resampled = df_resampled.dropna() if dropna else df_resampled.fillna(0)
        return df_resampled

    def _validate_params(self, request, raise_exception=True):
        params_serializer = CumulativeGraphQuerySerializer(data=request.query_params)
        params_serializer.is_valid(raise_exception=raise_exception)
        return params_serializer.validated_data

    @action(detail=False, methods=["get"], url_path="daily-profile")
    def daily_profile(self, request, *args, **kwargs):
        self.validated_params = self._validate_params(request, raise_exception=True)
        fields = self.validated_params["fields"]

        queryset = self.get_queryset()
        agg_queryset = queryset.aggregate_hourly("sum", fields)
        data = pd.DataFrame(list(agg_queryset))

        df = pd.DataFrame({"hour": range(24)})
        for field in fields:
            data_hourly = data.groupby("hour")[field].mean().reset_index()
            data_hourly[field] = data_hourly[field].apply(lambda x: round(x, 2))
            df = pd.concat([df, data_hourly[field]], axis=1)

        response_data = {
            "count": df.shape[0],
            "results": df.to_dict(orient="records"),
        }
        return Response(response_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="detail-daily-profile")
    def detail_daily_profile(self, request, *args, **kwargs):
        self.validated_params = self._validate_params(request, raise_exception=True)
        fields = self.validated_params["fields"]
        quarter_hourly_avg = self.get_queryset().quarter_hourly_avg(fields)
        serializer = DetailDailySerializer(quarter_hourly_avg, many=True, context={"fields": fields})

        response_data = {
            "count": quarter_hourly_avg.count(),
            "results": serializer.data,
        }
        return Response(response_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="peak_hours")
    def peak_hours(self, request, *args, **kwargs):
        self.validated_params = self._validate_params(request, raise_exception=True)
        fields = self.validated_params["fields"]
        peak_hours = self.get_queryset().aggregate_peak_hours(fields)
        return Response(peak_hours, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="off-peak-hours")
    def off_peak_hours(self, request, *args, **kwargs):
        self.validated_params = self._validate_params(request, raise_exception=True)
        fields = self.validated_params["fields"]
        off_peak_hours = self.get_queryset().aggregate_off_peak_hours(fields)
        return Response(off_peak_hours, status=status.HTTP_200_OK)


class ReportViewSet(viewsets.ReadOnlyModelViewSet):
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


class UferViewSet(viewsets.ReadOnlyModelViewSet):
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
