import logging

import pandas as pd
from django.conf import settings
from django.utils import timezone
from rest_framework import serializers

from apps.measurements.models import (
    CumulativeMeasurement,
    InstantMeasurement,
    ReferenceMeasurement,
)
from apps.measurements.services import CumulativeMeasurementManager
from apps.measurements.utils import get_error_messages
from apps.transductors.models import Transductor

logger = logging.getLogger("apps")


class InstantMeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstantMeasurement
        fields = [
            "id",
            "transductor",
            "frequency_a",
            "frequency_b",
            "frequency_c",
            "frequency_iec",
            "voltage_a",
            "voltage_b",
            "voltage_c",
            "current_a",
            "current_b",
            "current_c",
            "active_power_a",
            "active_power_b",
            "active_power_c",
            "total_active_power",
            "reactive_power_a",
            "reactive_power_b",
            "reactive_power_c",
            "total_reactive_power",
            "apparent_power_a",
            "apparent_power_b",
            "apparent_power_c",
            "total_apparent_power",
            "power_factor_a",
            "power_factor_b",
            "power_factor_c",
            "total_power_factor",
            "dht_voltage_a",
            "dht_voltage_b",
            "dht_voltage_c",
            "dht_current_a",
            "dht_current_b",
            "dht_current_c",
            "collection_date",
        ]


class RealTimeMeasurementSerializer(serializers.ModelSerializer):
    model = serializers.CharField(source="transductor.model.name")
    transductor_ip = serializers.CharField(source="transductor.ip_address")

    class Meta:
        model = InstantMeasurement
        fields = [
            "id",
            "transductor",
            "model",
            "transductor_ip",
            "voltage_a",
            "voltage_b",
            "voltage_c",
            "current_a",
            "current_b",
            "current_c",
            "total_active_power",
            "total_reactive_power",
            "total_power_factor",
            "collection_date",
        ]


class ReferenceMeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = CumulativeMeasurement
        fields = [
            "id",
            "transductor",
            "active_consumption",
            "active_generated",
            "reactive_inductive",
            "reactive_capacitive",
            "created",
            "updated",
        ]
        extra_kwargs = {"created": {"read_only": True}, "updated": {"read_only": True}}


class CumulativeMeasurementSerializer(serializers.ModelSerializer):
    collection_date = serializers.DateTimeField(default=timezone.now)

    class Meta:
        model = CumulativeMeasurement
        fields = [
            "id",
            "transductor",
            "active_consumption",
            "active_generated",
            "reactive_inductive",
            "reactive_capacitive",
            "collection_date",
        ]

    def create(self, validated_data):
        transductor = validated_data.get("transductor")
        last_measurement, created = ReferenceMeasurement.objects.get_or_create(transductor=transductor)
        fields = self.get_cumulative_fields()

        if created:
            data = validated_data.copy()
            data.update({field: 0 for field in fields})
            cumulative_measurements = super().create(data)
        else:
            cumulative_measurements = CumulativeMeasurementManager.handle_measurements(
                validated_data,
                last_measurement,
                fields,
            )

        try:
            self.update_reference_measurement(last_measurement, validated_data, fields)
        except Exception as e:
            print(f"Error updating reference measurement: {e}", flush=True)
            logger.error(f"Error updating reference measurement: {e}")
            raise ValueError("Error updating reference measurement")

        return cumulative_measurements

    def update_reference_measurement(self, last_measurement, validated_data, fields):
        for field in fields:
            if field in validated_data:
                setattr(last_measurement, field, validated_data[field])
        last_measurement.save()

    def get_cumulative_fields(self):
        return ["active_consumption", "active_generated", "reactive_inductive", "reactive_capacitive"]


class UferSerializer(serializers.Serializer):
    entity = serializers.CharField()
    month_year = serializers.DateField(format="%m-%Y")
    units = serializers.CharField()
    data = serializers.ListField()


class UferDetailSerializer(serializers.Serializer):
    transductor = serializers.IntegerField()
    ip = serializers.IPAddressField(source="transductor__ip_address")
    located = serializers.CharField(source="transductor__located__acronym")

    def to_representation(self, instance):
        data = super().to_representation(instance)

        fields = self.context.get("fields", {})
        for field in fields:
            len_total = instance.get(f"{field}_len_total", 0)
            len_quality = instance.get(f"{field}_len_quality", 0)
            percent = round((len_quality / len_total) * 100, 2) if len_total else 0.0
            data[f"pf_phase_{field[-1]}"] = percent
        return data


class ReportSerializer(serializers.Serializer):
    entity = serializers.CharField()
    month_year = serializers.DateField(format="%Y-%m")

    def __init__(self, *args, **kwargs):
        context = kwargs.get("context", {})
        fields = context.get("fields", [])
        super(ReportSerializer, self).__init__(*args, **kwargs)

        for field_name in fields:
            if field_name not in self.fields:
                self.fields[field_name] = serializers.FloatField(allow_null=True)


# =====================================================================================================================
#  Charts Serializers
# =====================================================================================================================


class GraphDataSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        """
        Format data for graph representation
        Example:
        {
            "information": {
                "time_zone": "America/Sao_Paulo",
                "date_format": "ISO-8601",
                "count": 4,
                "fields": ["voltage_a", "voltage_b", "voltage_c"]
            },

            "timestamp": ["2024-05-01T00:00:00.000Z", "2024-05-01T00:05:00.000Z", ...],
            "traces": [
                {
                    "field": "voltage_a",
                    "avg_value": 222.68,
                    "max_value": 227.05,
                    "min_value: 217.48,
                    "values": [
                        219.32,
                        227.05,
                        217.48
                    ]
                },
                {
                    "field": "voltage_b",
                    "count": 4,
                    "avg": 222.2,
                    "max_value": 226.27,
                    "min_value": 217.06,
                    "values": [
                        226.21,
                        226.27,
                        217.06
                    ]
                },
                ....
            ],
        }
        """
        tz = timezone.get_current_timezone()
        response = {
            "information": {
                "time_zone": timezone.get_current_timezone_name(),
                "date_format": "ISO-8601",
                "start_date": instance.collection_date.min().astimezone(tz).isoformat(),
                "end_date": instance.collection_date.max().astimezone(tz).isoformat(),
                "count": instance.shape[0],
                "fields": [field for field in instance.columns if field != "collection_date"],
            },
            "timestamp": [],
            "traces": [],
        }

        timestamp = instance.collection_date.apply(lambda ts: ts.astimezone(tz).isoformat())
        response["timestamp"] = timestamp.tolist()

        for field in response["information"]["fields"]:
            response["traces"].append(
                {
                    "field": field,
                    "avg_value": instance[field].mean().round(2),
                    "max_value": instance[field].max(),
                    "min_value": instance[field].min(),
                    "values": instance[field].tolist(),
                }
            )
        return response


# ---------------------------------------------------------------------------------------------------------------------
# Query Parameters Serializers
# ---------------------------------------------------------------------------------------------------------------------
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
    MODEL_ALLOWED_FIELDS = ["power_factor_a", "power_factor_b", "power_factor_c"]

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
    MODEL_ALLOWED_FIELDS = ["active_consumption", "active_generated", "reactive_inductive", "reactive_capacitive"]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if not attrs.get("fields"):
            attrs["fields"] = self.MODEL_ALLOWED_FIELDS
        return attrs
