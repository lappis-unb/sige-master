import logging

from django.core.management import BaseCommand
from django.core.management.base import CommandError, CommandParser
from django.utils import timezone

from measurements.models import EnergyTransductor, RealTimeMeasurement
from measurements.serializers import (
    MinutelyMeasurementSerializer,
    MonthlyMeasurementSerializer,
    QuarterlyMeasurementSerializer,
    RealTimeMeasurementSerializer,
)
from slaves.api import request_measurements
from slaves.models import Slave
from utils.helpers import log_execution_time, string_to_date

logger = logging.getLogger("tasks")

MEASUREMNT_TYPES = ("realtime", "minutely", "quarterly", "monthly")


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("measurement_type", type=str)

    @log_execution_time(logger, level=logging.INFO)
    def handle(self, *args, **options):
        measurement_type = options["measurement_type"]

        active_slaves = Slave.objects.filter(active=True, broken=False).count()
        message = f"Active servers: {active_slaves}" if active_slaves else "no active slave servers"
        logger.info(f"Data Collector - {message}")

        self.get_measurements(measurement_type)

    def get_measurements(self, measurement_type: str) -> int:
        if measurement_type not in MEASUREMNT_TYPES:
            logger.error(f"Unknown data_group: {measurement_type}")
            raise CommandError(f"Unknown data_group: {measurement_type}")

        slaves = Slave.objects.filter(active=True, broken=False)

        for slave in slaves:
            transductors = slave.transductors.filter(active=True, broken=False)

            logger.info(f"Starting {measurement_type} collection for {slave} : {slave.server_address}\n")
            logger.info(
                f"Transductors active: {len(transductors)}"
                if transductors
                else f"No active transductors in slave server: {slave}"
            )

            if measurement_type == "realtime":
                self.get_realtime_measurements(slave)
                continue

            for transductor in transductors:
                logger.info(f"Collecting transductor: {transductor} from slave: {slave} ")

                if measurement_type == "minutely":
                    self.get_minutely_measurements(slave, transductor)

                elif measurement_type == "quarterly":
                    self.get_quarterly_measurements(slave, transductor)

                elif measurement_type == "monthly":
                    self.get_monthly_measurements(slave, transductor)

                logger.debug("Finished Tranductor \n")

    def get_realtime_measurements(self, slave):
        realtime_measurements = request_measurements("/realtime-measurements/", slave)

        for measurement in realtime_measurements:
            self.build_realtime_measurements(measurement)

    def get_minutely_measurements(self, slave, transductor):
        start_date = transductor.last_minutely_collection
        minutely_measurements = request_measurements("/minutely-measurements/", slave, transductor.id, start_date)

        for measurement in minutely_measurements:
            self.build_minutely_measurements(measurement)

        transductor.last_minutely_collection = timezone.now()
        transductor.save()

    def get_quarterly_measurements(self, slave, transductor):
        start_date = transductor.last_quarterly_collection
        quarterly_measurements = request_measurements("/quarterly-measurements/", slave, transductor.id, start_date)

        for measurement in quarterly_measurements:
            self.build_quarterly_measurements(measurement)

        transductor.last_quarterly_collection = timezone.now()
        transductor.save()

    def get_monthly_measurements(self, slave, transductor):
        start_date = transductor.last_monthly_collection
        monthly_measurements = request_measurements("/monthly-measurements/", slave, transductor.id, start_date)

        for measurement in monthly_measurements:
            self.build_monthly_measurements(measurement, transductor)

        transductor.last_monthly_collection = timezone.now()
        transductor.save()

    def build_realtime_measurements(self, measurement):
        try:
            transductor = EnergyTransductor.objects.get(id=measurement["transductor"])
            realtime_measurement, _ = RealTimeMeasurement.objects.get_or_create(transductor=transductor)

            serializer = RealTimeMeasurementSerializer(realtime_measurement, data=measurement, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()

                logger.debug(
                    f"Saved measurement ID: {measurement['id']} - "
                    f"transductor: {measurement['transductor']} "
                    f"({string_to_date(measurement['collection_date'])})"
                )
        except Exception as e:
            logger.error(f"Failed to save RealTime measurement. Error: {str(e)}")

    def build_minutely_measurements(self, measurement):
        try:
            serializer = MinutelyMeasurementSerializer(data=measurement)
            if serializer.is_valid(raise_exception=True):
                serializer.save()

                logger.debug(
                    f"Saved measurement ID: {measurement['id']} - "
                    f"transductor: {measurement['transductor']} - "
                    f"{string_to_date(measurement['collection_date'])}"
                )
        except Exception as e:
            logger.error(f"Failed to save Minutely measurement. Error: {str(e)}")

    def build_quarterly_measurements(self, measurement):
        try:
            serializer = QuarterlyMeasurementSerializer(data=measurement)

            if serializer.is_valid(raise_exception=True):
                serializer.save()

                logger.debug(
                    f"Saved measurement ID: {measurement['id']}, "
                    f"Transductor: {measurement['transductor']}, "
                    f"{string_to_date(measurement['collection_date'])}"
                )
        except Exception as e:
            logger.error(f"Failed to save Quarterly measurement. Error: {str(e)}")

    def build_monthly_measurements(self, measurement, transductor):
        try:
            start_date = transductor.last_monthly_collection
            end_date = measurement["end_date"] or timezone.now()

            measurement["collection_date"] = end_date
            serializer = MonthlyMeasurementSerializer(data=measurement)

            if serializer.is_valid(raise_exception=True):
                serializer.save()

            num_days = (end_date.date() - start_date.date()).days
            reference_month = start_date.strftime("%B/%Y")

            logger.debug(
                f"Saved measurement transductor: {measurement['transductor']} - "
                f"Reference Month: {reference_month}, Num Days: {num_days}, "
            )
        except Exception as e:
            logger.error(f"Failed to save Monthly measurement. Error: {str(e)}")
