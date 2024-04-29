import logging
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, as_completed

from django.core.management import BaseCommand
from django.core.management.base import CommandError, CommandParser
from django.utils import timezone

from apps.measurements.serializers import (
    CumulativeMeasurementSerializer,
    InstantMeasurementSerializer,
)
from apps.memory_maps.modbus.data_reader import ModbusClientFactory
from apps.memory_maps.modbus.helpers import get_now
from apps.memory_maps.modbus.settings import (
    DATA_GROUP_CUMULATIVE,
    DATA_GROUP_INSTANT,
    DATA_GROUPS,
)
from apps.transductors.models import Transductor
from apps.utils.helpers import log_execution_time

logger = logging.getLogger("tasks")


class Command(BaseCommand):
    """
    This class defines a Django management command for collecting and saving data from a transductor.
    It inherits from Django's BaseCommand class for managing command-line arguments and output.
    """

    help = "Collects data from active transductors based on the specified data group."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("data_group", type=str)
        parser.add_argument("--max_workers", type=int, default=16)

    @log_execution_time(logger, level=logging.INFO)
    def handle(self, *args, **options):
        data_group = options["data_group"].lower().strip()
        max_workers = options["max_workers"]
        self.log_start(data_group, max_workers)

        active_transductors = Transductor.manager.active().select_related("model__memory_map")
        self.log_active_transductor(active_transductors)

        if data_group not in DATA_GROUPS:
            logger.error(f"Unknown data_group: {data_group}, exiting...")
            raise CommandError(f"Unknown data_group: {data_group}")

        if active_transductors.exists():
            modbus_data = self.process_collection(active_transductors, data_group, max_workers)
            self.save_data_to_database(modbus_data, data_group)
        else:
            logger.warning(f"No data was collected for the group {data_group}. Halting collect...")

    def process_collection(self, transductors, data_group, max_workers):
        """
        Collect data from each transductor in parallel.
        """
        if max_workers is None:
            max_workers = multiprocessing.cpu_count() * 4

        modbus_data = []
        # TODO - Testar no servidor de deploy diferentes valores para max_workers
        # TODO - Comparar ThreadPoolExecutor com ProcessPoolExecutor
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_list = []
            logger.debug("Starting data collection in parallel:")
            for transductor in transductors:
                future = executor.submit(self.collect_transductor_data, transductor, data_group)
                future_list.append(future)

            logger.debug("Finished data submission, collecting results:")
            for future in as_completed(future_list):
                try:
                    result = future.result()
                    if result["broken"]:
                        logger.error(f"{result['errors']} - changes status to BROKEN")
                    else:
                        logger.debug(f"Transductor: {result['collected']['transductor']}")
                        modbus_data.append(result["collected"])

                except Exception as e:
                    logger.error(f"ThreadPoolExecutor Error: {e}")
                    raise CommandError(f"{get_now()}  -  ThreadPoolExecutor Error: {e}")

        return modbus_data

    def collect_transductor_data(self, transductor, data_group) -> int:
        """
        Collect data from active transductors and save it to the database.
        """

        memory_map = transductor.model.memory_map
        register_blocks = memory_map.get_memory_map_by_type(data_group)

        modbus_collector = ModbusClientFactory(
            ip_address=transductor.ip_address,
            port=transductor.port,
            slave_id=transductor.model.modbus_addr_id,
            method=transductor.model.protocol,
        )

        modbus_data = {
            "collected": {},  # Dados coletados a partir do Modbus
            "errors": "",  # Mensagens de erro durante a coleta
            "broken": False,  # Indica se houve falha no medidor
        }

        try:
            collected_data = modbus_collector.read_datagroup_blocks(register_blocks)
            collected_data["transductor"] = transductor.id
            modbus_data["collected"] = collected_data
            logger.debug(f"Collected data from {transductor.model.name}")

        except Exception as e:
            modbus_data["broken"] = True
            modbus_data["errors"] = str(e)
            logger.error(f"Errors: {modbus_data['errors']}")
            transductor.set_broken(notes=str(e))
            logger.info(f"Deactivating transductor: {transductor.current_status}")
        return modbus_data

    def save_data_to_database(self, modbus_data, data_group) -> None:
        """
        Save the provided modbus_data to the database using the provided serializer class.
        """
        serializer_class = self.get_serializer_class(data_group)
        serializer = serializer_class(data=modbus_data, many=True)

        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            valid_data = self.partition_valid_and_error_data(serializer)

            if not valid_data:
                logger.warning(f"{get_now()} - No valid data to save in the database")
                return

            serializer = serializer_class(data=valid_data, many=True)
            serializer.is_valid(raise_exception=True)

        serializer.save()
        self.log_report(serializer, data_group)

    def get_serializer_class(self, data_group: str):
        serializer_class = {
            DATA_GROUP_INSTANT: InstantMeasurementSerializer,
            DATA_GROUP_CUMULATIVE: CumulativeMeasurementSerializer,
        }
        return serializer_class.get(data_group)

    def partition_valid_and_error_data(self, serializer):
        """
        Partition data into valid entries and error details based on serializer validation.
        More detailed error contexts and structured error handling.
        """
        valid_data = []
        for error, data in zip(serializer.errors, serializer.initial_data):
            if not error:
                valid_data.append(data)
            else:
                error_message = {
                    "error": error,
                    "data": data,
                    "timestamp": timezone.now().isoformat(),
                }

                logger.error(f"Data validation error: {error_message}")

        return valid_data

    def log_start(self, data_group, max_workers):
        logger.info(f"   Data collector - {data_group.upper()}")
        logger.debug(f"   MultiThread - Cores: {multiprocessing.cpu_count()}")
        logger.debug(f"   MultiThread - Max workers: {max_workers}")
        logger.debug("-" * 85)

    def log_active_transductor(self, transductor):
        if transductor.exists():
            logger.info(f"Active Transductors: {transductor.count()}")
        else:
            logger.warning("No active Transductors in database")

    def log_report(self, serializer, data_group):
        if logger.level == logging.DEBUG:
            data_group = data_group.capitalize()
            logger.info(f"[{len(serializer.data)}] Collects completed and saved database.")
            for data in serializer.data:
                logger.debug(f"transductor: {data['transductor']} - {data_group} Measurement: {data['id']}")
