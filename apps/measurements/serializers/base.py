import logging

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
            "is_calculated",
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
