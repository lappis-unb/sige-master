from django.contrib import admin
from . import models


@admin.register(models.Slave)
class SlaveAdmin(admin.ModelAdmin):
    list_display = (
        'broken',
        'ip_address',
        'port',
        'location',
    )

    list_filter = (
        'broken',
    )
