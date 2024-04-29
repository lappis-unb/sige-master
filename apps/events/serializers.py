from rest_framework import serializers

from apps.events.models import (
    CategoryEvent,
    CompareOperator,
    Event,
    EventType,
    MeasurementTrigger,
    MeasurementType,
    SeverityEvent,
)
from apps.utils.helpers import get_dynamic_fields


class EventTypeSerializer(serializers.ModelSerializer):
    severity = serializers.ChoiceField(choices=SeverityEvent.choices)
    category = serializers.ChoiceField(choices=CategoryEvent.choices)

    class Meta:
        model = EventType
        fields = (
            "id",
            "name",
            "code",
            "severity",
            "category",
        )


class MeasurementTriggerSerializer(serializers.ModelSerializer):
    measurement_type = serializers.ChoiceField(choices=MeasurementType.choices)
    operator = serializers.ChoiceField(choices=CompareOperator.choices)

    class Meta:
        model = MeasurementTrigger
        fields = [
            "id",
            "field_name",
            "measurement_type",
            "upper_limit",
            "lower_limit",
            "operator",
            "debouce_time",
        ]


class EventSerializer(serializers.ModelSerializer):
    field_name = serializers.SerializerMethodField()
    measurement_type = serializers.SerializerMethodField()
    upper_limit = serializers.SerializerMethodField()
    lower_limit = serializers.SerializerMethodField()
    operator = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            "id",
            "is_active",
            "created_at",
            "ended_at",
            "transductor",
            "event_type",
            "measurement_trigger",
            "field_name",
            "measurement_type",
            "upper_limit",
            "lower_limit",
            "operator",
        ]
        read_only_fields = ["id", "created_at", "ended_at"]

    def get_field_name(self, obj):
        return obj.measurement_trigger.field_name

    def get_measurement_type(self, obj):
        return obj.measurement_trigger.get_measurement_type_display()

    def get_upper_limit(self, obj):
        return obj.measurement_trigger.upper_limit

    def get_lower_limit(self, obj):
        return obj.measurement_trigger.lower_limit

    def get_operator(self, obj):
        return obj.measurement_trigger.get_operator_display()
