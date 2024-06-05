import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.events.models import CumulativeMeasurementTrigger, InstantMeasurementTrigger
from apps.events.services import TriggerService
from apps.measurements.models import CumulativeMeasurement, InstantMeasurement

logger = logging.getLogger("apps")


@receiver(post_save, sender=CumulativeMeasurement)
def handle_cumulative_trigger(sender, instance, created, **kwargs):
    if created:
        logger.info("Cumulative measurement created")
        triggers = CumulativeMeasurementTrigger.objects.filter(is_active=True)
        if not triggers:
            logger.info("No active triggers found for Cumulative measurement")
            return

        logger.info(f"Processing triggers for {instance.transductor.ip_address}")
        for trigger in triggers:
            trigger_service = TriggerService(trigger, instance)
            trigger_service.perform_trigger()


@receiver(post_save, sender=InstantMeasurement)
def handle_instant_trigger(sender, instance, created, **kwargs):
    if created:
        logger.info("Instant measurement created")
        triggers = InstantMeasurementTrigger.objects.filter(is_active=True)
        if not triggers:
            logger.info("No active triggers found for Instant measurement")
            return

        logger.info(f"Processing triggers for {instance.transductor.ip_address}")
        for trigger in triggers:
            trigger_service = TriggerService(trigger, instance)
            trigger_service.perform_trigger()
