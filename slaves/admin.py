from django.contrib import admin

from . import models


@admin.register(models.Slave)
class SlaveAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "server_address",
        "port",
        "broken",
        "active",
    )

    list_filter = ("broken", "active")
