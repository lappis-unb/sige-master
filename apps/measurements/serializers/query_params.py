import logging

import pandas as pd
from django.conf import settings
from django.utils import timezone
from rest_framework import serializers

from apps.measurements.models import CumulativeMeasurement, InstantMeasurement
from apps.measurements.serializers.utils import get_error_messages

logger = logging.getLogger("apps.measurements.serializers.query_params")


class BaseQuerySerializer(serializers.Serializer):
    start_date = serializers.DateTimeField(error_messages=get_error_messages("date"))
    end_date = serializers.DateTimeField(error_messages=get_error_messages("date"))
    period = serializers.CharField(error_messages=get_error_messages())
    fields = serializers.CharField(error_messages=get_error_messages())

    MODEL_ALLOWED_FIELDS = []
    REQUIRED_PARAMETERS = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field not in self.REQUIRED_PARAMETERS:
                self.fields[field].required = False

    def validate_period(self, value):
        try:
            value = pd.to_timedelta(value)
        except ValueError as e:
            raise serializers.ValidationError(f"Invalid period format. {e}")
        return value

    def validate_fields(self, value: str):
        fields = value.split(",")
        invalid_fields = set(fields) - set(self.MODEL_ALLOWED_FIELDS)

        if invalid_fields:
            raise serializers.ValidationError(
                f"Cannot resolve fields: {', '.join(invalid_fields)}, "
                f"Choices are: {', '.join(self.MODEL_ALLOWED_FIELDS)}."
            )
        return fields

    def validate(self, attrs):
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date", timezone.now())
        period = attrs.get("period")

        if start_date and start_date > end_date:
            raise serializers.ValidationError("Start date must be earlier than end date.")

        if period and start_date:
            raise serializers.ValidationError("You can't use 'start_date' and 'period' parameters together.")

        return attrs


class InstantMeasurementQuerySerializer(BaseQuerySerializer):
    transductor = serializers.IntegerField(min_value=1, error_messages=get_error_messages("integer"))

    REQUIRED_PARAMETERS = ["transductor"]
    MODEL_ALLOWED_FIELDS = [
        str(field.name)
        for field in InstantMeasurement._meta.fields
        if field.name not in {"id", "collection_date", "transductor"}
    ]


class CumulativeMeasurementQuerySerializer(BaseQuerySerializer):
    transductor = serializers.IntegerField(min_value=1, error_messages=get_error_messages("integer"))

    REQUIRED_PARAMETERS = ["transductor"]
    MODEL_ALLOWED_FIELDS = [
        str(field.name)
        for field in CumulativeMeasurement._meta.fields
        if field.name not in {"id", "collection_date", "transductor", "is_calculated"}
    ]


class InstantGraphQuerySerializer(BaseQuerySerializer):
    transductor = serializers.IntegerField(min_value=1, error_messages=get_error_messages("integer"))
    lttb = serializers.BooleanField(default=True, required=False)
    threshold = serializers.IntegerField(min_value=2, default=settings.LIMIT_FILTER, required=False)

    REQUIRED_PARAMETERS = ["transductor", "fields"]
    MODEL_ALLOWED_FIELDS = [
        str(field.name)
        for field in InstantMeasurement._meta.fields
        if field.name not in {"id", "collection_date", "transductor", "is_calculated"}
    ]

    def validate_lttb(self, value):
        if not isinstance(value, bool):
            raise serializers.ValidationError("Invalid value for 'lttb' parameter. Use 'true' or 'false'.")
        return bool(value)


class CumulativeGraphQuerySerializer(BaseQuerySerializer):
    transductor = serializers.IntegerField(min_value=1, error_messages=get_error_messages("integer"))
    freq = serializers.CharField(required=False)
    agg = serializers.CharField(required=False)

    REQUIRED_PARAMETERS = ["transductor", "fields"]
    MODEL_ALLOWED_FIELDS = [
        str(field.name)
        for field in CumulativeMeasurement._meta.fields
        if field.name not in {"id", "collection_date", "transductor", "is_calculated"}
    ]

    def validate_freq(self, value):
        try:
            time_delta = pd.to_timedelta(value)
        except ValueError:
            raise serializers.ValidationError("Invalid frequency format. Use ISO 8601 duration format.")

        if time_delta.total_seconds() < 900:
            raise serializers.ValidationError("Invalid frequency. Use a minimum of 15 minutes.")
        return time_delta

    def validate_agg(self, value):
        if value not in ["sum", "mean", "max", "min"]:
            raise serializers.ValidationError("Invalid aggregation function. Use 'sum', 'mean', 'max' or 'min'.")
        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if bool(attrs.get("freq")) ^ bool(attrs.get("agg")):
            raise serializers.ValidationError("You must provide 'freq' and 'agg' parameters together.")
        return attrs


class UferQuerySerializer(BaseQuerySerializer):
    entity = serializers.IntegerField(min_value=1, required=True)
    inc_desc = serializers.BooleanField(default=True, required=False)
    depth = serializers.IntegerField(min_value=0, default=0, required=False)
    th_percent = serializers.IntegerField(min_value=1, max_value=100, default=92, required=False)
    only_day = serializers.BooleanField(required=False)

    REQUIRED_PARAMETERS = ["entity"]
    MODEL_ALLOWED_FIELDS = [
        "power_factor_a",
        "power_factor_b",
        "power_factor_c",
    ]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if not attrs.get("fields"):
            attrs["fields"] = self.MODEL_ALLOWED_FIELDS
        return attrs

    def validate_period(self, value):
        value = super().validate_period(value)

        if value > pd.Timedelta("30 days"):
            raise serializers.ValidationError("The maximum period allowed is 30 days.")


class ReportQuerySerializer(BaseQuerySerializer):
    entity = serializers.IntegerField(min_value=1)
    inc_desc = serializers.BooleanField(default=True)
    depth = serializers.IntegerField(min_value=0, default=0)

    REQUIRED_PARAMETERS = ["entity"]
    MODEL_ALLOWED_FIELDS = [
        "active_consumption",
        "active_generated",
        "reactive_inductive",
        "reactive_capacitive",
    ]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if not attrs.get("fields"):
            attrs["fields"] = self.MODEL_ALLOWED_FIELDS
        return attrs
