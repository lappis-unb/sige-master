from django.apps import AppConfig


class DataCollectorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = "apps.memory_maps"
    verbose_name = "Memory Maps module"
