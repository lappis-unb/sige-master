import logging

import pandas as pd
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.measurements.filters import (
    CumulativeMeasurementFilter,
    DailyProfileFilter,
    InstantMeasurementFilter,
)
from apps.measurements.models import CumulativeMeasurement, InstantMeasurement
from apps.measurements.serializers import (
    CumulativeGraphQuerySerializer,
    CumulativeMeasurementQuerySerializer,
    DailyProfileQuerySerializer,
    DailyProfileSerializer,
    GraphDataSerializer,
    InstantGraphQuerySerializer,
)
from apps.measurements.services.downsampler import LTTBDownSampler

logger = logging.getLogger("apps.measurements.views.graph")


@extend_schema(parameters=[InstantGraphQuerySerializer])
class InstantGraphViewSet(ListModelMixin, GenericViewSet):
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


@extend_schema(parameters=[CumulativeMeasurementQuerySerializer])
class CumulativeGraphViewSet(ListModelMixin, GenericViewSet):
    queryset = CumulativeMeasurement.objects.all()
    serializer_class = GraphDataSerializer
    query_params_class = CumulativeGraphQuerySerializer
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
        params_serializer = self.query_params_class(data=request.query_params)
        params_serializer.is_valid(raise_exception=raise_exception)
        return params_serializer.validated_data


@extend_schema(parameters=[DailyProfileQuerySerializer])
class DailyProfileViewSet(CumulativeGraphViewSet):
    serializer_class = DailyProfileSerializer
    query_params_class = DailyProfileQuerySerializer
    filterset_class = DailyProfileFilter

    def list(self, request, *args, **kwargs):
        self.validated_params = self._validate_params(request, raise_exception=True)
        fields = self.validated_params.get("fields")
        detail = self.validated_params.get("detail")
        queryset = self.get_queryset()
        response_data = self._aggregate_data(queryset, fields, detail)
        if not response_data:
            return Response({"detail": "No data found."}, status=status.HTTP_204_NO_CONTENT)
        serializer = self.get_serializer(response_data, many=True, context={"fields": fields})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def _aggregate_data(self, queryset, fields, detail):
        if detail:
            return queryset.quarter_hourly_avg(fields)

        aggregate_qs = queryset.aggregate_hourly("sum", fields, adjust_hour=False)
        if not aggregate_qs:
            return []

        data = pd.DataFrame(list(aggregate_qs))
        grouped_data = data.groupby("hour")[fields].mean().reset_index()
        grouped_data[fields] = grouped_data[fields].astype(float).round(4)
        return grouped_data.to_dict(orient="records")
