import logging
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, as_completed

from django.core.management.base import BaseCommand, CommandParser
from pymodbus.client.tcp import ModbusTcpClient
from pymodbus.exceptions import ConnectionException

from apps.transductors.models import Status, Transductor
from apps.utils.helpers import log_execution_time

logger = logging.getLogger("tasks")


class Command(BaseCommand):
    help = "Test all transducers."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--max_workers", type=int, default=8)

    @log_execution_time(logger, level=logging.INFO)
    def handle(self, *args, **options) -> None:
        max_workers = options["max_workers"]
        transductors = Transductor.objects.broken_and_non_status()
        self.log_start(transductors, max_workers)

        if transductors.exists():
            self.process_broken_transductors(transductors, options["max_workers"])
        else:
            logger.info("Halted. No broken transducers found.")

    def process_broken_transductors(self, transductors, max_workers):
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_list = []
            for transductor in transductors:
                future = executor.submit(self.check_transductor, transductor)
                future_list.append(future)

            for future in as_completed(future_list):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Error processing transductor: {e}")

    def check_transductor(self, transductor):
        """Tests the connection to a transducer."""

        client = ModbusTcpClient(transductor.ip_address, transductor.port)
        try:
            if client.connect():
                logger.info(f"Connection SUCCESS to transducer at: {transductor.ip_address}:{transductor.port}")
                self.activate_transductor(transductor)
            else:
                logger.error(f"Connection FAILED to transducer at: {transductor.ip_address}:{transductor.port}")
                self.deactivate_transductor(transductor)

        except ConnectionException as e:
            logger.error(f"Connection Error to transducer at: {transductor.ip_address}:{transductor.port} - {str(e)}")

        finally:
            client.close()

    def activate_transductor(self, transductor: Transductor) -> None:
        logger.info(f"Activated transducer: {transductor.ip_address}:{transductor.port}.")
        transductor.set_status(Status.ACTIVE, "Connection test successful.")

    def deactivate_transductor(self, transductor):
        logger.info(f"Deactivated transducer: {transductor.ip_address}:{transductor.port}.")
        transductor.set_status(Status.BROKEN, "Connection test failed.")

    def log_start(self, transductors, max_workers):
        logger.info("   Check Transductors - Starting...")
        logger.debug(f"   MultiThread - Cores: {multiprocessing.cpu_count()}")
        logger.debug(f"   MultiThread - Max workers: {max_workers}")
        logger.debug("-" * 85)

        if transductors.exists():
            logger.info(f"Broken Transductors: {transductors.count()}")
        else:
            logger.warning("No broken transducers found.")
