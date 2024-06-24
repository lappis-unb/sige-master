from rest_framework import serializers

from apps.events.models import (
    CumulativeMeasurementTrigger,
    Event,
    InstantMeasurementTrigger,
    Trigger,
)


class TriggerSerializer(serializers.ModelSerializer):
    severity = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = Trigger
        fields = (
            "id",
            "name",
            "severity",
            "category",
            "is_active",
            "created_at",
        )

    def get_severity(self, obj):
        return obj.get_severity_display()

    def get_category(self, obj):
        return obj.get_category_display()


class InstantMeasurementTriggerSerializer(TriggerSerializer):
    class Meta:
        model = InstantMeasurementTrigger
        fields = TriggerSerializer.Meta.fields + (
            "field_name",
            "lower_threshold",
            "upper_threshold",
        )
        read_only_fields = ["id", "created_at", "updated_at"]


class CumulativeMeasurementTriggerSerializer(TriggerSerializer):
    class Meta:
        model = CumulativeMeasurementTrigger
        fields = TriggerSerializer.Meta.fields + (
            "field_name",
            "dynamic_metric",
            "lower_threshold_percent",
            "upper_threshold_percent",
            "period_days",
        )


class EventSerializer(serializers.ModelSerializer):
    field_name = serializers.SerializerMethodField()
    lower_threshold = serializers.SerializerMethodField()
    upper_threshold = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    severity = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            "id",
            "trigger",
            "transductor",
            "name",
            "field_name",
            "severity",
            "category",
            "lower_threshold",
            "upper_threshold",
            "created_at",
            "ended_at",
            "is_active",
        ]
        read_only_fields = ["id", "created_at", "ended_at"]

    def get_field_name(self, obj):
        if hasattr(obj.trigger, "instantmeasurementtrigger"):
            return obj.trigger.instantmeasurementtrigger.field_name
        elif hasattr(obj.trigger, "cumulativemeasurementtrigger"):
            return obj.trigger.cumulativemeasurementtrigger.field_name
        else:
            return None

    def get_lower_threshold(self, obj):
        if hasattr(obj.trigger, "instantmeasurementtrigger"):
            return obj.trigger.instantmeasurementtrigger.lower_threshold
        elif hasattr(obj.trigger, "cumulativemeasurementtrigger"):
            return obj.trigger.cumulativemeasurementtrigger.lower_threshold_percent
        else:
            return None

    def get_upper_threshold(self, obj):
        if hasattr(obj.trigger, "instantmeasurementtrigger"):
            return obj.trigger.instantmeasurementtrigger.upper_threshold
        elif hasattr(obj.trigger, "cumulativemeasurementtrigger"):
            return obj.trigger.cumulativemeasurementtrigger.upper_threshold_percent
        else:
            return None

    def get_severity(self, obj):
        return obj.trigger.get_severity_display()

    def get_category(self, obj):
        return obj.trigger.get_category_display()
