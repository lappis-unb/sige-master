from django import forms
from django.contrib import admin

from apps.events.models import (
    CumulativeMeasurementTrigger,
    Event,
    EventType,
    InstantMeasurementTrigger,
    MeasurementTrigger,
)
from apps.utils.helpers import get_dynamic_fields


class MeasurementTriggerAdmin(admin.ModelAdmin):
    list_display = (
        "measurement_type",
        "field_name",
        "upper_limit",
        "lower_limit",
        "operator",
        "debouce_time",
        "is_active",
    )
    list_filter = ("measurement_type", "operator", "is_active")
    search_fields = ("is_active", "field_name")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "event_type",
                    "field_name",
                    "measurement_type",
                    "operator",
                    "upper_limit",
                    "lower_limit",
                    "debouce_time",
                    "is_active",
                    "notes",
                )
            },
        ),
    )


@admin.register(InstantMeasurementTrigger)
class InstantMeasurementTriggerAdmin(MeasurementTriggerAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["measurement_type"].widget = forms.HiddenInput()
        dynamic_instant_fields = get_dynamic_fields("measurements", "InstantMeasurement")

        if dynamic_instant_fields:
            field = form.base_fields["field_name"]
            field.choices = dynamic_instant_fields
            field.widget = forms.Select(choices=dynamic_instant_fields)
        return form


# Similar logic for CumulativeMeasurementTriggerAdmin (if needed)
@admin.register(CumulativeMeasurementTrigger)
class CumulativeMeasurementTriggerAdmin(MeasurementTriggerAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["measurement_type"].widget = forms.HiddenInput()  # Hide measurement_type
        dynamic_cumulative_fields = get_dynamic_fields("measurements", "CumulativeMeasurement")

        if dynamic_cumulative_fields:
            field = form.base_fields["field_name"]
            field.choices = dynamic_cumulative_fields
            field.widget = forms.Select(choices=dynamic_cumulative_fields)
        return form


# ---------------------------------------------------------------------------------------------------------------------


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "get_severity_display", "get_category_display")
    list_filter = ("severity", "category")
    search_fields = ("name", "code")

    def get_severity_display(self, obj):
        return obj.get_severity_display()

    get_severity_display.short_description = "Severity"

    def get_category_display(self, obj):
        return obj.get_category_display()

    get_category_display.short_description = "Category"


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "event_type",
        "get_trigger_id",
        "transductor",
        "measurement_trigger_measurement_type",
        "measurement_trigger_field_name",
        "measurement_trigger_upper_limit",
        "measurement_trigger_lower_limit",
        "measurement_trigger_operator",
        "created_at",
        "ended_at",
        "is_active",
    )
    list_filter = ("is_active", "event_type__category", "event_type__severity")
    search_fields = (
        "event_type__name",
        "transductor__name",
    )
    readonly_fields = ("created_at", "ended_at")
    actions = ["close_events"]

    def close_events(self, request, queryset):
        for event in queryset.filter(is_active=True):
            event.close_event()
        self.message_user(request, "Selected events have been closed.")

    close_events.short_description = "Close selected events"

    def get_trigger_id(self, obj):
        return obj.measurement_trigger.pk if obj.measurement_trigger else None

    get_trigger_id.short_description = "Trigger ID"

    def get_measurement_trigger_instance(self, obj):
        if obj.measurement_trigger:
            return MeasurementTrigger.objects.filter(pk=obj.measurement_trigger.pk).first()
        return None

    def measurement_trigger_field_name(self, obj):
        measurement_trigger = self.get_measurement_trigger_instance(obj)
        return measurement_trigger.field_name if measurement_trigger else None

    measurement_trigger_field_name.short_description = "Field Name"

    def measurement_trigger_measurement_type(self, obj):
        measurement_trigger = self.get_measurement_trigger_instance(obj)
        return measurement_trigger.measurement_type if measurement_trigger else None

    measurement_trigger_measurement_type.short_description = "Measurement Type"

    def measurement_trigger_upper_limit(self, obj):
        measurement_trigger = self.get_measurement_trigger_instance(obj)
        return measurement_trigger.upper_limit if measurement_trigger else None

    measurement_trigger_upper_limit.short_description = "Upper Limit"

    def measurement_trigger_lower_limit(self, obj):
        measurement_trigger = self.get_measurement_trigger_instance(obj)
        return measurement_trigger.lower_limit if measurement_trigger else None

    measurement_trigger_lower_limit.short_description = "Lower Limit"

    def measurement_trigger_operator(self, obj):
        measurement_trigger = self.get_measurement_trigger_instance(obj)
        return measurement_trigger.operator if measurement_trigger else None

    measurement_trigger_operator.short_description = "Operator"
