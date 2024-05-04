from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.events.models import (
    CumulativeMeasurementTrigger,
    Event,
    EventType,
    InstantMeasurementTrigger,
    Trigger,
)


@admin.register(Trigger)
class TriggerAdmin(admin.ModelAdmin):
    list_display = ("name", "event_type", "is_active", "created_at", "updated_at")
    list_filter = ("event_type", "is_active")
    search_fields = ("name", "event_type__name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(InstantMeasurementTrigger)
class InstantMeasurementTriggerAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "is_active",
        "event_type",
        "field_name",
        "operator",
        "active_threshold",
        "deactivate_threshold",
    )
    list_filter = ("is_active", "event_type", "operator")
    search_fields = ("name", "field_name")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "event_type",
                    "field_name",
                    "operator",
                    "active_threshold",
                    "deactivate_threshold",
                    "notes",
                    "is_active",
                )
            },
        ),
    )


@admin.register(CumulativeMeasurementTrigger)
class CumulativeMeasurementTriggerAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "is_active",
        "event_type",
        "field_name",
        "dynamic_metric",
        "adjustment_factor",
        "period_days",
    )
    list_filter = ("is_active", "event_type", "dynamic_metric")
    search_fields = ("name", "field_name")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "event_type",
                    "field_name",
                    "dynamic_metric",
                    "adjustment_factor",
                    "period_days",
                    "notes",
                    "is_active",
                ),
            },
        ),
    )


# ---------------------------------------------------------------------------------------------------------------------


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "get_severity_display", "get_category_display")
    list_filter = ("severity", "category")
    search_fields = ("name", "code")

    def get_severity_display(self, obj):
        return obj.get_severity_display()

    get_severity_display.short_description = _("Severity")

    def get_category_display(self, obj):
        return obj.get_category_display()

    get_category_display.short_description = _("Category")


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("event_type", "transductor", "created_at", "ended_at", "is_active")
    list_filter = ("is_active", "event_type__category", "event_type__severity")
    search_fields = ("event_type__name", "transductor__name")
    readonly_fields = ("created_at", "ended_at")
    date_hierarchy = "created_at"
    actions = ["close_events"]

    def close_events(self, request, queryset):
        for event in queryset:
            if event.is_active:
                event.close_event()
        self.message_user(request, _("Selected events have been closed."))

    close_events.short_description = _("Close selected events")
