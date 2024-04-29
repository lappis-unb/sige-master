import logging

from app.events.services import TriggerService
from django.core.management import BaseCommand
from utils.helpers import log_execution_time

logger = logging.getLogger("tasks")


@log_execution_time(logger, level=logging.INFO)
class Command(BaseCommand):
    help = "Perform triggers service to proccess events."

    def add_arguments(self, parser):
        parser.add_argument(
            "--transductor",
            type=int,
            help="Transductor ID to process triggers.",
        )
        parser.add_argument(
            "--event",
            type=int,
            help="Event ID to process triggers.",
        )
        parser.add_argument(
            "--trigger",
            type=int,
            help="Trigger ID to process triggers.",
        )

    def handle(self, *args, **kwargs):
        trigger_id = kwargs.get("trigger")
        event_id = kwargs.get("event")
        transductor_id = kwargs.get("transductor")

        if trigger_id:
            trigger = Trigger.objects.get(id=trigger_id)

        # trigger_service = TriggerService(trigger, instance)
        # trigger_service.perform_trigger()
