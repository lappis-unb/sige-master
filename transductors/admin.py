from django.contrib import admin
from . import models


@admin.register(models.EnergyTransductor)
class EnergyTransductorAdmin(admin.ModelAdmin):
    list_display = (
        'serial_number',
        'ip_address',
        'physical_location',
        'firmware_version',
        'name',
        'broken',
        'active',
        'calibration_date',
    )

    list_filter = (
        'broken',
        'active',
        'firmware_version',
    )
