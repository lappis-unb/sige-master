from django.contrib import admin
from . import models


@admin.register(models.Slave)
class SlaveAdmin(admin.ModelAdmin):
    list_display = (
        'ip_address',
        'port',
        'location',
        'broken',
    )

    list_filter = (
        'broken',
    )
