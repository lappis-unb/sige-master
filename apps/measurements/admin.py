from django.contrib import admin

from apps.measurements.models import (
    CumulativeMeasurement,
    InstantMeasurement,
    ReferenceMeasurement,
)


@admin.register(InstantMeasurement)
class InstantMeasurementMeasurementAdmin(admin.ModelAdmin):
    list_display = (
        "transductor",
        "collection_date",
        "voltage_a",
        "frequency_a",
        "current_a",
        "active_power_a",
        "reactive_power_a",
        "apparent_power_a",
        "power_factor_a",
    )
    list_filter = ("collection_date", "transductor")
    search_fields = ("transductor__ip_address", "total_active_power")
    fieldsets = (
        (None, {"fields": ("transductor",)}),
        ("Frequencies", {"fields": ("frequency_a", "frequency_b", "frequency_c", "frequency_iec")}),
        ("Voltages", {"fields": ("voltage_a", "voltage_b", "voltage_c")}),
        ("Currents", {"fields": ("current_a", "current_b", "current_c")}),
        (
            "Powers",
            {
                "fields": (
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
                )
            },
        ),
        (
            "Distortion",
            {
                "fields": (
                    "dht_voltage_a",
                    "dht_voltage_b",
                    "dht_voltage_c",
                    "dht_current_a",
                    "dht_current_b",
                    "dht_current_c",
                )
            },
        ),
    )


@admin.register(CumulativeMeasurement)
class CumulativeMeasurementAdmin(admin.ModelAdmin):
    list_display = (
        "transductor",
        "collection_date",
        "active_consumption",
        "active_generated",
        "reactive_inductive",
        "reactive_capacitive",
        "is_calculated",
    )
    list_filter = ("collection_date", "transductor")
    search_fields = ("transductor__ip_address", "total_active_power")
    fieldsets = (
        (None, {"fields": ("transductor",)}),
        (
            "Powers",
            {
                "fields": (
                    "active_consumption",
                    "active_generated",
                    "reactive_inductive",
                    "reactive_capacitive",
                )
            },
        ),
    )


@admin.register(ReferenceMeasurement)
class ReferenceMeasurementAdmin(admin.ModelAdmin):
    list_display = (
        "transductor",
        "active_consumption",
        "active_generated",
        "reactive_inductive",
        "reactive_capacitive",
        "created",
        "updated",
    )
    list_filter = ("updated", "transductor")
    search_fields = ("transductor__ip_address", "total_active_power")
    fieldsets = (
        (None, {"fields": ("transductor",)}),
        (
            "Powers",
            {
                "fields": (
                    "active_consumption",
                    "active_generated",
                    "reactive_inductive",
                    "reactive_capacitive",
                )
            },
        ),
    )
