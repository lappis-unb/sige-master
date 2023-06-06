from django.contrib import admin
from . import models


@admin.register(models.EnergyTransductor)
class EnergyTransductorAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "model",
        "ip_address",
        "port",
        "serial_number",
        "active",
        "broken",
        "pending_sync",
        "pending_deletion",
    )

    list_filter = (
        "broken",
        "active",
    )
