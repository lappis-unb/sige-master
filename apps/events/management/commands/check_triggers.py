import logging

from django.core.management import BaseCommand

from apps.utils.helpers import log_execution_time

logger = logging.getLogger("tasks")


@log_execution_time(logger, level=logging.INFO)
class Command(BaseCommand):
    help = "Perform triggers service to process events."

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
