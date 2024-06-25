import logging

from django.core.management.base import BaseCommand

from apps.events.models import TransductorStatusTrigger
from apps.events.services import TransductorEventManager
from apps.utils.helpers import log_execution_time

logger = logging.getLogger("tasks")


class Command(BaseCommand):
    help = "Perform triggers service to process transductor status."

    @log_execution_time(logger, level=logging.INFO)
    def handle(self, *args, **options) -> None:
        triggers = TransductorStatusTrigger.objects.filter(is_active=True).order_by("-threshold_time")
        if not triggers.exists():
            logger.info("Halted. No active triggers found.")
            return

        logger.info(f"\tProcessing {triggers.count()} active triggers...")

        transductor_event_manager = TransductorEventManager()
        try:
            transductor_event_manager.perform_triggers(triggers)
        except Exception as e:
            logger.error(f"Error processing triggers: {e}")
