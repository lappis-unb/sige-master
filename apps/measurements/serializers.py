import logging
import dateutil
from django.utils import timezone
from rest_framework import serializers

from apps.measurements.models import (
    CumulativeMeasurement,
    InstantMeasurement,
    ReferenceMeasurement,
)
from apps.measurements.services import CumulativeMeasurementManager

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

# ---------------------------------------------------------------------------------------------------------------------
# Query Serializers
# ---------------------------------------------------------------------------------------------------------------------
class BaseQuerySerializer(serializers.Serializer):
    entity = serializers.IntegerField(min_value=1, required=True)
    month_year = serializers.CharField(default=timezone.now().strftime("%m-%Y"))
    descendants = serializers.BooleanField(default=True, required=False)
    depth = serializers.IntegerField(min_value=0, default=0, required=False)
    fields = serializers.CharField(default=None, required=False)

    ALLOWED_FIELDS = []

    def validate_fields(self, value):
        if value is None:
            return self.ALLOWED_FIELDS

        fields = [field.strip() for field in value.split(",")] if value else []
        for field in fields:
            if field not in self.ALLOWED_FIELDS:
                raise serializers.ValidationError(
                    f"The field '{field}' is not allowed.Allowed fields: {self.ALLOWED_FIELDS}"
                )
        return fields

    def validate_month_year(self, value):
        try:
            return dateutil.parser.parse(value, default=timezone.now()).date()
        except ValueError:
            raise serializers.ValidationError("Invalid date format for 'month_year'. Use 'YYYY-MM' or 'MM-YYYY'.")


class UferQuerySerializer(BaseQuerySerializer):
    ALLOWED_FIELDS = ["power_factor_a", "power_factor_b", "power_factor_c"]


class ReportQuerySerializer(BaseQuerySerializer):
    ALLOWED_FIELDS = ["active_consumption", "active_generated", "reactive_inductive", "reactive_capacitive"]


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
                "fields": ["voltage_a", "voltage_b", "voltage_c"]
            },

            "timestamp": ["2024-05-01T00:00:00.000Z", "2024-05-01T00:05:00.000Z", ...],
            "traces": [
                {
                    "field": "voltage_a",
                    "count": 4,
                    "avg": 222.68,
                    "max_value": 227.05,
                    "min_value": 217.48,
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
        response = {
            "information": {
                "time_zone": timezone.get_current_timezone_name(),
                "date_format": "ISO-8601",
                "count": instance.shape[0],
                "fields": [field for field in instance.columns if field != "collection_date"],
            },
            "timestamp": [],
            "traces": [],
        }

        timestamp = instance.collection_date.apply(lambda x: x.astimezone(timezone.get_current_timezone()).isoformat())
        response["timestamp"] = timestamp.tolist()

        for field in response["information"]["fields"]:
            response["traces"].append(
                {
                    "field": field,
                    "count": instance.shape[0],
                    "avg": instance[field].mean().round(2),
                    "max": instance[field].max(),
                    "min": instance[field].min(),
                    "values": instance[field].tolist(),
                }
            )

        return response
