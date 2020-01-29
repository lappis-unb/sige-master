from django.contrib import admin
from . import models


@admin.register(models.EnergyTransductor)
class EnergyTransductorAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'model',
        'ip_address',
        'serial_number',
        'active',
        'broken',
    )

    list_filter = (
        'broken',
        'active',
    )
