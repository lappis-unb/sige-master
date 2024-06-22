from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.events.models import (
    CumulativeMeasurementTrigger,
    Event,
    InstantMeasurementTrigger,
    Trigger,
)


@admin.register(Trigger)
class TriggerAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "severity",
        "category",
        "is_active",
        "created_at",
        "updated_at",
    )
    list_filter = ("category", "is_active", "severity")
    search_fields = ("name", "notification_message")
    readonly_fields = ("created_at", "updated_at")


@admin.register(InstantMeasurementTrigger)
class InstantMeasurementTriggerAdmin(TriggerAdmin):
    list_display = TriggerAdmin.list_display + (
        "field_name",
        "operator",
        "active_threshold",
        "deactivate_threshold",
        "notification_message",
    )
    list_filter = TriggerAdmin.list_filter + ("operator", "field_name")
    search_fields = TriggerAdmin.search_fields + ("field_name",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "severity",
                    "category",
                    "field_name",
                    "operator",
                    "active_threshold",
                    "deactivate_threshold",
                    "notification_message",
                    "is_active",
                )
            },
        ),
    )


@admin.register(CumulativeMeasurementTrigger)
class CumulativeMeasurementTriggerAdmin(TriggerAdmin):
    list_display = TriggerAdmin.list_display + (
        "field_name",
        "dynamic_metric",
        "adjustment_factor",
        "period_days",
        "notification_message",
    )
    list_filter = TriggerAdmin.list_filter + ("dynamic_metric", "field_name")
    search_fields = TriggerAdmin.search_fields + ("field_name",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "severity",
                    "category",
                    "field_name",
                    "operator",
                    "dynamic_metric",
                    "adjustment_factor",
                    "period_days",
                    "notification_message",
                    "is_active",
                ),
            },
        ),
    )


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "display_name",
        "display_severity",
        "display_category",
        "transductor",
        "created_at",
        "ended_at",
        "is_active",
    )
    readonly_fields = (
        "created_at",
        "ended_at",
        "display_name",
        "display_severity",
        "display_category",
    )
    list_filter = ("is_active", "transductor")
    search_fields = ("name", "transductor__name")
    date_hierarchy = "created_at"
    actions = ["close_events"]

    def display_name(self, obj):
        return obj.name

    display_name.short_description = _("Name")

    def display_severity(self, obj):
        return obj.severity

    display_severity.short_description = _("Severity")

    def display_category(self, obj):
        return obj.category

    display_category.short_description = _("Category")

    def close_events(self, request, queryset):
        for event in queryset:
            if event.is_active:
                event.close_event()
        self.message_user(request, _("Selected events have been closed."))

    close_events.short_description = _("Close selected events")
