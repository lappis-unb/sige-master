from django.contrib import admin

from apps.memory_maps.models import MemoryMap


@admin.register(MemoryMap)
class MemoryMapAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "model",
        "instant_measurements",
        "cumulative_measurements",
        "created_at",
        "updated_at",
    ]
