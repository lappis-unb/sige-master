from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.transductors.models import StatusHistory, Transductor, TransductorModel


@admin.register(TransductorModel)
class TransductorModelAdmin(admin.ModelAdmin):
    list_display = (
        "manufacturer",
        "name",
        "protocol",
        "read_function",
        "modbus_addr_id",
        "max_block_size",
        "base_address",
        "memory_map_file",
        "created",
        "updated",
    )
    list_filter = ("manufacturer", "protocol", "read_function")
    search_fields = ("name", "manufacturer", "modbus_addr_id")
    ordering = ("name", "manufacturer")
    readonly_fields = ("created", "updated")

    fieldsets = (
        (_("Identification"), {"fields": ("manufacturer", "name")}),
        (
            _("Configuration"),
            {
                "fields": (
                    "protocol",
                    "read_function",
                    "modbus_addr_id",
                    "max_block_size",
                    "base_address",
                    "memory_map_file",
                )
            },
        ),
        (_("Additional Information"), {"fields": ("notes", "created", "updated")}),
    )

    def protocol_display(self, obj):
        return obj.get_protocol_display()

    protocol_display.short_description = _("Protocol")

    def read_function_display(self, obj):
        return obj.get_read_function_display()

    read_function_display.short_description = _("Read Function")

    def notes_short(self, obj):
        return f"{obj.notes[:75]}..." if len(obj.notes) > 75 else obj.notes

    notes_short.short_description = _("Notes")


@admin.register(Transductor)
class TransductorAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "model",
        "get_status",
        "serial_number",
        "ip_address",
        "port",
        "located",
    ]
    list_display_links = ("id", "model")
    search_fields = ("id", "model", "serial_number", "ip_address")
    list_filter = ("model", "ip_address")

    def get_status(self, obj):
        return obj.current_status

    get_status.short_description = "status"

    fields = (
        "model",
        "serial_number",
        "ip_address",
        "port",
        "located",
        "geo_location",
    )


@admin.register(StatusHistory)
class StatusHistoryAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "transductor",
        "status",
        "start_time",
        "end_time",
        "duration",
        "notes",
    ]

    list_display_links = ("id", "transductor")
    search_fields = ("transductor", "start_time", "end_time", "status")
    list_filter = ("transductor", "start_time", "end_time", "status")

    readonly_fields = ("start_time", "end_time", "duration")
