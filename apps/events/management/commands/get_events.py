import logging

from django.core.management import BaseCommand

from utils.helpers import log_execution_time

logger = logging.getLogger("tasks")


@log_execution_time(logger, level=logging.INFO)
class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        logger.info("Get events started:")
        logger.info("Not implemented yet...........")
        logger.info("Get events finished")
