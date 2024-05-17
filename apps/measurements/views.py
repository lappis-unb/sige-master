import logging

import pandas as pd
from django.conf import settings
from django.db.models import Case, Count, Q, Sum, When
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
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
    CumulativeMeasurementQuerySerializer,
    CumulativeMeasurementSerializer,
    GraphDataSerializer,
    InstantMeasurementQuerySerializer,
    InstantMeasurementSerializer,
    ReportQuerySerializer,
    ReportSerializer,
    UferDetailSerializer,
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
    filter_backends = [DjangoFilterBackend]
    filterset_class = InstantMeasurementFilter
    pagination_class = MeasurementPagination

    @action(detail=False, methods=["get"], url_path="export-csv")
    def export_csv(self, request):
        params_serializer = InstantMeasurementQuerySerializer(data=request.query_params)
        params_serializer.is_valid(raise_exception=True)
        validated_params = params_serializer.validated_data

        queryset = self.filter_queryset(self.get_queryset())
        fields = validated_params.get("fields", [])
        return generate_csv_response(queryset, fields=fields, filename="instant_measurements.csv")


class CumulativeMeasurementViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CumulativeMeasurementSerializer
    queryset = CumulativeMeasurement.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = CumulativeMeasurementFilter
    pagination_class = MeasurementPagination

    @action(detail=False, methods=["get"], url_path="export-csv")
    def export_csv(self, request):
        params_serializer = CumulativeMeasurementQuerySerializer(data=request.query_params)
        params_serializer.is_valid(raise_exception=True)
        validated_params = params_serializer.validated_data

        queryset = self.filter_queryset(self.get_queryset())
        fields = validated_params.get("fields", [])
        return generate_csv_response(queryset, fields=fields, filename="cumulative_measurements.csv")


class InstantGraphViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InstantMeasurement.objects.all()
    serializer_class = GraphDataSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = InstantMeasurementFilter

    def list(self, request, *args, **kwargs):
        query_params = self.get_query_params()
        self.validate_params(query_params)

        queryset = self.get_queryset(fields=query_params["fields"])
        if not queryset:
            return Response(status=status.HTTP_204_NO_CONTENT)

        df = pd.DataFrame(list(queryset))
        lttb = query_params["lttb"].lower() == "true"
        response = self.apply_lttb(df) if lttb else df
        serializer = self.get_serializer(response)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_query_params(self):
        fields = self.request.query_params.get("fields", "")
        return {
            "fields": fields.split(",") if fields else [],
            "transductor": self.request.query_params.get("transductor", None),
            "lttb": self.request.query_params.get("lttb", None),
            "threshold": self.request.query_params.get("threshold", settings.LIMIT_FILTER),
        }

    def validate_params(self, query_params):
        required_params = ["transductor", "fields"]
        missing_params = [param for param in required_params if query_params.get(param) is None]

        if missing_params:
            message = f"Missing required parameters: {', '.join(missing_params)}"
            logger.error(f"Error: {message}")
            raise ValidationError({"error": message})

    def get_queryset(self, *args, **kwargs):
        fields = kwargs.get("fields", [])
        try:
            queryset = super().get_queryset().values("collection_date", *fields)
        except Exception as e:
            logger.error(f"Error in get_queryset: {e}")
            raise ValidationError({"error": str(e)})
        return self.filter_queryset(queryset)

    def apply_lttb(self, df):
        threshold = int(self.request.query_params.get("threshold", settings.LIMIT_FILTER))
        try:
            downsampler = LTTBDownSampler(threshold, enable_parallel=False)
            return downsampler.apply_lttb(df, dt_column="collection_date")
        except Exception as e:
            logger.error(f"Error in apply_lttb: {e}")
            raise ValidationError({"error": str(e)})


class CumulativeGraphViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CumulativeMeasurement.objects.all()
    serializer_class = GraphDataSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CumulativeMeasurementFilter

    def list(self, request, *args, **kwargs):
        query_params = self.get_query_params()
        self.validate_params(query_params)

        queryset = self.get_queryset(field=query_params["field"])
        if not queryset.exists():
            return Response({"detail": "No data found."}, status=status.HTTP_204_NO_CONTENT)

        data = pd.DataFrame(list(queryset))
        response = self.apply_resample(data, query_params["period"], query_params["method"])
        serializer = self.get_serializer(response)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_query_params(self):
        return {
            "transductor": self.request.query_params.get("transductor", None),
            "field": self.request.query_params.get("field", None),
            "period": self.request.query_params.get("period", "PT15M"),
            "method": self.request.query_params.get("method", "sum"),
        }

    def validate_params(self, query_params):
        required_params = ["transductor", "field"]
        missing_params = [param for param in required_params if query_params.get(param) is None]

        if missing_params:
            message = f"Missing required parameters: {', '.join(missing_params)}"
            logger.error(f"Error: {message}")
            raise ValidationError({"error": message})

    def get_queryset(self, *args, **kwargs):
        field = self.request.query_params.get("field", None)
        try:
            queryset = super().get_queryset().values("collection_date", field)
        except Exception as e:
            logger.error(f"Error in get_queryset: {e}")
            raise ValidationError({"error": str(e)})
        return self.filter_queryset(queryset)

    def apply_resample(self, df, period, method, dropna=True):
        if not period or period == "PT15M":
            return df
        try:
            rule = self.get_resample_frequency(period)
        except Exception as e:
            logger.error(f"Error in apply_resample: {e}")
            raise ValidationError({"error": str(e)})

        df_resampled = df.resample(rule, on="collection_date").apply(method)
        df_resampled = df_resampled.reset_index()

        if dropna:
            df_resampled.dropna(inplace=True)
        return df_resampled

    def get_resample_frequency(self, period):
        frequency = pd.Timedelta(period)
        if frequency is None:
            raise ValueError(f"Invalid period format: '{period}'. Use ISO8601 duration format (PT<value><unit>).")

        elif frequency.total_seconds() < 900:
            raise ValueError(f"Invalid period value: '{period}'. Minimum value is 15 minutes 'PT15M'.")
        logger.debug(f"Resampling rule determined: {frequency.total_seconds() // 60} minutes")
        return frequency

    @action(detail=False, methods=["get"])
    def hourly(self, request, *args, **kwargs):
        query_params = self.get_query_params()
        self.validate_params(query_params)

        queryset = self.get_queryset(field=query_params["field"])
        if not queryset.exists():
            return Response(status=status.HTTP_204_NO_CONTENT)

        data = pd.DataFrame(list(queryset))
        data.set_index("collection_date", inplace=True)
        data_hourly = data.resample("h").apply("sum")

        data_hourly = data_hourly.groupby(data_hourly.index.hour).mean()
        data_hourly = data_hourly.reset_index()
        data_hourly.rename(columns={"collection_date": "hour"}, inplace=True)
        data_hourly.rename(columns={query_params["field"]: "value"}, inplace=True)

        responde = {
            "field": query_params["field"],
            "start_date": data.index[0],
            "end_date": data.index[-1],
            "data": data_hourly.to_dict(orient="records"),
        }

        return Response(responde, status=status.HTTP_200_OK)


class ReportViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CumulativeMeasurement.objects.all()
    serializer_class = ReportSerializer

    def get_queryset(self, *args, **kwargs):
        try:
            return super().get_queryset().values("collection_date", *kwargs.get("fields"))
        except Exception as e:
            logger.error(f"Error in get_queryset: {e}")
            raise ValidationError({"error": str(e)})

    def list(self, request, *args, **kwargs):
        query_serializer = ReportQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)
        validated_params = query_serializer.validated_data

        queryset = self.get_queryset(fields=validated_params["fields"])
        if not queryset:
            Response({"detail": "No data found."}, status=status.HTTP_204_NO_CONTENT)

        entity = get_object_or_404(Entity, pk=validated_params.get("entity"))
        transductor_ids = self._get_transductors_entities(entity, validated_params)
        month_year = validated_params.get("month_year")

        measurements = queryset.filter(
            transductor__in=transductor_ids,
            collection_date__year=month_year.year,
            collection_date__month=month_year.month,
        )

        response_data = self._aggregate_data(measurements, validated_params["fields"])
        response_data["month_year"] = month_year
        response_data["entity"] = entity.name
        serializer = self.get_serializer(data=response_data, context={"fields": validated_params["fields"]})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def _aggregate_data(self, queryset, fields):
        aggregates = {field: Sum(field) for field in fields}
        return queryset.aggregate(**aggregates)

    def _get_transductors_entities(self, entity, params):
        if params.get("descendants"):
            entities = entity.get_descendants(include_self=True, max_depth=params.get("depth"))
            return Transductor.objects.filter(located__in=entities).values_list("id", flat=True)
        return [entity.id]


class UferViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InstantMeasurement.objects.all()
    serializer_class = UferSerializer

    def get_queryset(self, *args, **kwargs):
        return (
            super()
            .get_queryset()
            .exclude(power_factor_a=0, power_factor_b=0, power_factor_c=0)
            .only(*kwargs.get("fields", "collection_date", "transductor"))
        )

    def list(self, request, *args, **kwargs):
        query_serializer = UferQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)
        validated_params = query_serializer.validated_data
        fields = validated_params["fields"]

        queryset = self.get_queryset(fields=fields)
        if not queryset:
            Response({"detail": "No data found."}, status=status.HTTP_204_NO_CONTENT)

        entity = get_object_or_404(Entity, pk=validated_params.get("entity"))
        transductor_ids = self._get_transductors_entities(entity, validated_params)
        month_year = validated_params.get("month_year")

        measurements = self.get_queryset().filter(
            transductor__in=transductor_ids,
            collection_date__year=month_year.year,
            collection_date__month=month_year.month,
        )

        aggregated_data = list(self._aggregate_data(measurements, fields))
        detail_serializer = UferDetailSerializer(aggregated_data, many=True, context={"fields": fields})

        response_data = {
            "entity": entity.name,
            "month_year": month_year,
            "units": "percentage",
            "data": detail_serializer.data,
        }

        response_serializer = self.get_serializer(data=response_data)
        response_serializer.is_valid(raise_exception=True)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def _get_transductors_entities(self, entity, params):
        if params.get("descendants"):
            entities = entity.get_descendants(include_self=True, max_depth=params.get("depth"))
            return Transductor.objects.filter(located__in=entities).values_list("id", flat=True)
        return [entity.id]

    def _aggregate_data(self, queryset, fields):
        filter_conditions = self._generate_filter_conditions(fields)
        annotations = self._generate_annotations(fields, filter_conditions)
        return queryset.values(
            "transductor",
            "transductor__ip_address",
            "transductor__located__acronym",
        ).annotate(**annotations)

    def _generate_filter_conditions(self, fields, threshold=0.92):
        conditions = Q()
        for field in fields:
            conditions |= Q(**{f"{field}__gt": 0.92}) | Q(**{f"{field}__lt": -0.92})
        return conditions

    def _generate_annotations(self, fields, filter_conditions):
        annotations = {}
        for field in fields:
            annotations[f"{field}_len_total"] = Count(field)
            annotations[f"{field}_len_quality"] = Count(Case(When(filter_conditions, then=1)))
        return annotations
