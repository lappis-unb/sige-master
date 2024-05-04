from rest_framework import serializers

from apps.events.models import (  # Event,
    CategoryEvent,
    CompareOperator,
    CumulativeMeasurementTrigger,
    EventType,
    InstantMeasurementTrigger,
    SeverityEvent,
    Trigger,
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


class TriggerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trigger
        fields = (
            "id",
            "name",
            "event_type",
            "is_active",
            "notes",
            "created_at",
            "updated_at",
        )


class InstantMeasurementTriggerSerializer(TriggerSerializer):
    operator = serializers.ChoiceField(choices=CompareOperator.choices)
    # field = serializers.ChoiceField(choices=get_dynamic_fields("measurements", "InstantMeasurement"))
    field = serializers.SerializerMethodField()

    class Meta:
        model = InstantMeasurementTrigger
        fields = TriggerSerializer.Meta.fields + (
            "field",
            "operator",
            "active_threshold",
            "deactivate_threshold",
        )
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_field(self, obj):
        return obj.measurement_trigger.field_name


class CumulativeMeasurementTriggerSerializer(TriggerSerializer):
    field = serializers.ChoiceField(choices=get_dynamic_fields("measurements", "CumulativeMeasurement"))

    class Meta:
        model = CumulativeMeasurementTrigger
        fields = TriggerSerializer.Meta.fields + (
            "field",
            "dynamic_metric",
            "adjustment_factor",
            "period_days",
        )


# class EventSerializer(serializers.ModelSerializer):
#     field_name = serializers.SerializerMethodField()
#     measurement_type = serializers.SerializerMethodField()
#     upper_limit = serializers.SerializerMethodField()
#     lower_limit = serializers.SerializerMethodField()
#     operator = serializers.SerializerMethodField()

#     class Meta:
#         model = Event
#         fields = [
#             "id",
#             "is_active",
#             "created_at",
#             "ended_at",
#             "transductor",
#             "event_type",
#             "measurement_trigger",
#             "field_name",
#             "measurement_type",
#             "upper_limit",
#             "lower_limit",
#             "operator",
#         ]
#         read_only_fields = ["id", "created_at", "ended_at"]

#     def get_field_name(self, obj):
#         return obj.measurement_trigger.field_name

#     def get_measurement_type(self, obj):
#         return obj.measurement_trigger.get_measurement_type_display()

#     def get_upper_limit(self, obj):
#         return obj.measurement_trigger.upper_limit

#     def get_lower_limit(self, obj):
#         return obj.measurement_trigger.lower_limit

#     def get_operator(self, obj):
#         return obj.measurement_trigger.get_operator_display()
