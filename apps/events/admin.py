from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.translation import gettext_lazy as _

from apps.events.models import (
    CategoryTrigger,
    CumulativeMeasurementTrigger,
    Event,
    InstantMeasurementTrigger,
    SeverityTrigger,
    TransductorStatusTrigger,
    Trigger,
)
from apps.transductors.models import Transductor


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
        "id",
        "field_name",
        "lower_threshold",
        "upper_threshold",
        "notification_message",
    )
    list_filter = TriggerAdmin.list_filter + ("field_name",)
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
                    "lower_threshold",
                    "upper_threshold",
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
        "upper_threshold_percent",
        "lower_threshold_percent",
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
                    "dynamic_metric",
                    "upper_threshold_percent",
                    "lower_threshold_percent",
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
        "trigger__pk",
        "transductor",
        "display_name",
        "trigger__field_name",
        "trigger__target_status",
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
        severity = obj.severity
        return SeverityTrigger(severity).label

    display_severity.short_description = _("Severity")

    def display_category(self, obj):
        category = obj.category
        return CategoryTrigger(category).label

    display_category.short_description = _("Category")

    def close_events(self, request, queryset):
        for event in queryset:
            if event.is_active:
                event.close_event()
        self.message_user(request, _("Selected events have been closed."))

    close_events.short_description = _("Close selected events")

    def trigger__pk(self, obj):
        return obj.trigger.pk

    trigger__pk.short_description = _("Trigger ID")

    def trigger__field_name(self, obj):
        if obj.trigger.instantmeasurementtrigger:
            return obj.trigger.instantmeasurementtrigger.field_name
        elif obj.trigger.cumulativemeasurementtrigger:
            return obj.trigger.cumulativemeasurementtrigger.field_name
        return "N/A"

    trigger__field_name.short_description = _("Field Name")

    def trigger__target_status(self, obj):
        if obj.trigger.transductorstatustrigger:
            return obj.trigger.transductorstatustrigger.get_target_status_display()
        return "N/A"

    trigger__target_status.short_description = _("Target Status")


# ______________________________________________________________________________


class TransductorStatusTriggerForm(forms.ModelForm):
    transductors = forms.ModelMultipleChoiceField(
        queryset=Transductor.objects.all(),
        required=False,
        blank=True,
        widget=FilteredSelectMultiple(_("Transductors"), is_stacked=False),
    )

    class Meta:
        model = TransductorStatusTrigger
        fields = "__all__"


@admin.register(TransductorStatusTrigger)
class TransductorStatusTriggerAdmin(admin.ModelAdmin):
    form = TransductorStatusTriggerForm
    list_display = (
        "name",
        "target_status",
        "severity",
        "category",
        "threshold_time",
        # "display_transductors",
        "is_active",
        "created_at",
    )
    list_filter = ("category", "is_active", "severity", "category")
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "severity",
                    "category",
                    "target_status",
                    "transductors",
                    "threshold_time",
                    "is_active",
                    "notification_message",
                )
            },
        ),
    )

    def display_transductors(self, obj):
        return ", ".join([transductor.ip_address for transductor in obj.transductors.all()])

    display_transductors.short_description = _("Transductors")

    def target_state(self, obj):
        return obj.get_target_status_display()

    target_state.short_description = _("Target State")
