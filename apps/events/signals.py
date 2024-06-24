import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.events.models import CumulativeMeasurementTrigger, InstantMeasurementTrigger
from apps.events.services import MeasurementEventManager
from apps.measurements.models import CumulativeMeasurement, InstantMeasurement

logger = logging.getLogger("apps")


@receiver(post_save, sender=InstantMeasurement)
def handle_instant_trigger(sender, instance, created, **kwargs):
    if not created:
        return
    logger.debug("Instant measurement created")
    active_triggers = InstantMeasurementTrigger.objects.filter(is_active=True)
    if not active_triggers.exists():
        logger.debug("No active triggers found for Instant measurement")
        return

    field_names = active_triggers.values_list("field_name", flat=True).distinct()
    for field_name in field_names:
        field_triggers = active_triggers.filter(field_name=field_name)

        field_value = getattr(instance, field_name, None)
        if field_value is None:
            logger.debug(f"No value for field '{field_name}' - skipping triggers")
            continue

        event_manager = MeasurementEventManager(instance, field_name)
        event_manager.perform_triggers(field_triggers)


@receiver(post_save, sender=CumulativeMeasurement)
def handle_cumulative_trigger(sender, instance, created, **kwargs):
    if not created:
        return

    logger.debug("Cumulative measurement created")
    active_triggers = CumulativeMeasurementTrigger.objects.filter(is_active=True)
    if not active_triggers.exists():
        logger.debug("No active triggers found for Cumulative measurement")
        return

    field_names = active_triggers.values_list("field_name", flat=True).distinct()
    for field_name in field_names:
        field_triggers = active_triggers.filter(field_name=field_name)

        field_value = getattr(instance, field_name, None)
        if field_value is None:
            logger.debug(f"No value for field '{field_name}' - skipping triggers")
            continue

        logger.debug(f"Processing triggers for {field_name} for {instance.transductor.ip_address}")

        event_manager = MeasurementEventManager(instance, field_name)
        event_manager.perform_triggers(field_triggers)
