from django.contrib import admin
from . import models


@admin.register(models.Campus)
class CampusAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'acronym',
        'phone',
        'address',
        'website_address',
    )
