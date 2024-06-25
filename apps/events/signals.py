import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.events.models import (
    CumulativeMeasurementTrigger,
    Event,
    InstantMeasurementTrigger,
    TransductorStatusTrigger,
)
from apps.events.services import MeasurementEventManager
from apps.measurements.models import CumulativeMeasurement, InstantMeasurement
from apps.transductors.models import StatusHistory

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


@receiver(post_save, sender=StatusHistory)
def handle_status_history(sender, instance, created, **kwargs):
    if not created:
        return

    logger.debug("Status history created")
    active_triggers = TransductorStatusTrigger.objects.filter(is_active=True)
    if not active_triggers.exists():
        logger.debug("No active triggers found for Status history")
        return

    previous_instance = (
        StatusHistory.objects.filter(transductor=instance.transductor)  #
        .exclude(pk=instance.pk)
        .order_by("-id")
        .first()
    )

    for trigger in active_triggers:
        logger.debug(f"Trigger target status: {trigger.get_target_status_display()}")

        if previous_instance.status == trigger.target_status:
            logger.info(f"Previous status matches trigger target status: {trigger.get_target_status_display()}")
            event = Event.objects.filter(transductor=instance.transductor, trigger=trigger, is_active=True).first()

            if event:
                event.close_event()
                logger.info(f"Event {event.id} closed: conditions no longer met!")
            else:
                logger.info(f"No active event found for trigger on {instance.transductor}")
