import logging

import pandas as pd
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
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
    CumulativeGraphQuerySerializer,
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


@extend_schema(parameters=[CumulativeGraphQuerySerializer])
class CumulativeGraphViewSet(ListModelMixin, GenericViewSet):
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

    @extend_schema(responses={200: DailyProfileSerializer(many=True)})
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

        response_data = df.to_dict(orient="records")
        serializer = DailyProfileSerializer(response_data, many=True, context={"fields": fields})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={200: DailyProfileSerializer(many=True)})
    @action(detail=False, methods=["get"], url_path="detail-daily-profile")
    def detail_daily_profile(self, request, *args, **kwargs):
        self.validated_params = self._validate_params(request, raise_exception=True)
        fields = self.validated_params["fields"]
        quarter_hourly_qs = self.get_queryset().quarter_hourly_avg(fields)
        serializer = DailyProfileSerializer(quarter_hourly_qs, many=True, context={"fields": fields})
        return Response(serializer.data, status=status.HTTP_200_OK)

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
