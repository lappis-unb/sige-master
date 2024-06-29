import logging

import pandas as pd
from django.utils import timezone
from rest_framework import serializers

from apps.measurements.models import CumulativeMeasurement, InstantMeasurement
from apps.measurements.serializers.utils import field_params

logger = logging.getLogger("apps.measurements.serializers.query_params")


class BaseQuerySerializer(serializers.Serializer):
    start_date = serializers.DateTimeField(**field_params("date"))
    end_date = serializers.DateTimeField(**field_params("date"))
    fields = serializers.CharField(**field_params("fields"))

    class Meta:
        required_parameters = []
        model_allowed_fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field not in self.Meta.required_parameters:
                self.fields[field].required = False

    def validate_fields(self, value: str):
        fields = value.split(",")
        invalid_fields = set(fields) - set(self.Meta.model_allowed_fields)

        if invalid_fields:
            raise serializers.ValidationError(
                {
                    "fields": f"Invalid fields: {', '.join(invalid_fields)}. "
                    f"Choices are: {', '.join(self.Meta.model_allowed_fields)}."
                }
            )
        return fields

    def validate(self, attrs):
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date", timezone.now())

        if start_date and start_date > end_date:
            raise serializers.ValidationError({"start_date": "Start must be before end date (current time if unset)."})

        return attrs


class InstantMeasurementQuerySerializer(BaseQuerySerializer):
    transductor = serializers.IntegerField(min_value=1, **field_params("transductor"))

    class Meta:
        required_parameters = ["transductor"]
        model_allowed_fields = [
            str(field.name)
            for field in InstantMeasurement._meta.fields
            if field.name not in {"id", "collection_date", "transductor"}
        ]


class CumulativeMeasurementQuerySerializer(BaseQuerySerializer):
    transductor = serializers.IntegerField(min_value=1, **field_params("transductor"))

    class Meta:
        required_parameters = ["transductor"]
        model_allowed_fields = [
            str(field.name)
            for field in CumulativeMeasurement._meta.fields
            if field.name not in {"id", "collection_date", "transductor", "is_calculated"}
        ]


class InstantGraphQuerySerializer(InstantMeasurementQuerySerializer):
    lttb = serializers.BooleanField(required=False, **field_params("lttb"))
    threshold = serializers.IntegerField(min_value=2, required=False, **field_params("threshold"))
    only_day = serializers.BooleanField(required=False, **field_params("only_day"))

    class Meta:
        required_parameters = ["transductor", "fields"]
        model_allowed_fields = InstantMeasurementQuerySerializer.Meta.model_allowed_fields

    def validate_lttb(self, value):
        if not isinstance(value, bool):
            raise serializers.ValidationError("Invalid value for 'lttb' parameter. Use 'true' or 'false'.")
        return bool(value)


class DailyProfileQuerySerializer(CumulativeMeasurementQuerySerializer):
    detail = serializers.BooleanField(required=False, **field_params("detail_profile"))
    peak_hours = serializers.BooleanField(required=False, **field_params("peak_hours"))
    off_peak_hours = serializers.BooleanField(required=False, **field_params("off_peak_hours"))

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs.get("peak_hours") and attrs.get("off_peak_hours"):
            raise serializers.ValidationError("You can't use 'peak_hours' and 'off_peak_hours' parameters together.")

        if not attrs.get("fields"):
            attrs["fields"] = self.Meta.model_allowed_fields
        return attrs


class CumulativeGraphQuerySerializer(CumulativeMeasurementQuerySerializer):
    freq = serializers.CharField(required=False, **field_params("freq"))
    agg = serializers.CharField(required=False, **field_params("agg"))
    only_day = serializers.BooleanField(required=False, **field_params("only_day"))

    class Meta:
        required_parameters = ["transductor", "fields"]
        model_allowed_fields = CumulativeMeasurementQuerySerializer.Meta.model_allowed_fields

    def validate_freq(self, value):
        try:
            time_delta = pd.to_timedelta(value)
        except ValueError:
            raise serializers.ValidationError({"freq": "Invalid frequency format. Use ISO 8601 duration format."})

        if time_delta.total_seconds() < 900:
            raise serializers.ValidationError({"freq": "Invalid frequency. Use a minimum of 15 minutes."})
        return time_delta

    def validate_agg(self, value):
        if value not in ["sum", "mean", "max", "min"]:
            raise serializers.ValidationError(
                {"agg": "Invalid aggregation function. Use 'sum', 'mean', 'max' or 'min'."}
            )
        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if bool(attrs.get("freq")) ^ bool(attrs.get("agg")):
            raise serializers.ValidationError("You must provide 'freq' and 'agg' parameters together.")
        return attrs


class UferQuerySerializer(BaseQuerySerializer):
    transductor = serializers.IntegerField(min_value=1, **field_params("transductor"))
    entity = serializers.IntegerField(min_value=1, **field_params("entity"))
    inc_desc = serializers.BooleanField(required=False, **field_params("inc_desc"))
    max_depth = serializers.IntegerField(min_value=0, required=False, **field_params("depth"))
    only_day = serializers.BooleanField(required=False, **field_params("only_day"))
    th_percent = serializers.IntegerField(
        min_value=1,
        max_value=100,
        required=False,
        **field_params("th_percent"),
    )

    class Meta:
        required_parameters = ["entity", "start_date", "end_date"]
        model_allowed_fields = ["power_factor_a", "power_factor_b", "power_factor_c"]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if not attrs.get("fields"):
            attrs["fields"] = self.Meta.model_allowed_fields

        if attrs.get("start_date") and (attrs.get("end_date") - attrs.get("start_date")).days > 31:
            raise serializers.ValidationError("The maximum period allowed is 31 days.")

        return attrs


class ReportQuerySerializer(BaseQuerySerializer):
    transductor = serializers.IntegerField(min_value=1, **field_params("transductor"))
    entity = serializers.IntegerField(min_value=1, **field_params("entity"))
    inc_desc = serializers.BooleanField(**field_params("inc_desc"))
    only_day = serializers.BooleanField(required=False, **field_params("only_day"))
    depth = serializers.IntegerField(min_value=0, **field_params("depth"))
    detail = serializers.BooleanField(**field_params("detail_report"))

    class Meta:
        required_parameters = ["entity", "start_date", "end_date"]
        model_allowed_fields = [
            "active_consumption",
            "active_generated",
            "reactive_inductive",
            "reactive_capacitive",
        ]
        model_default_fields = [
            "active_consumption",
            "active_generated",
        ]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if not attrs.get("fields"):
            attrs["fields"] = self.Meta.model_default_fields

        if attrs.get("start_date") and (attrs.get("end_date") - attrs.get("start_date")).days > 31:
            raise serializers.ValidationError("The maximum period allowed is 31 days.")

        return attrs
