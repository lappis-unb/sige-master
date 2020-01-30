from django.contrib import admin
from . import models


@admin.register(models.Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'type',
    )

    list_filter = (
        'type'
    )


@admin.register(models.GroupType)
class GroupTypeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
    )
