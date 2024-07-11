from django.apps import AppConfig


class MeasurementsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.measurements"
    verbose_name = "Measurements module"

    def ready(self):
        from apps.events.models import (
            CumulativeMeasurementTrigger,
            InstantMeasurementTrigger,
        )

        InstantMeasurementTrigger.init_choices()
        CumulativeMeasurementTrigger.init_choices()
