import json
import logging

from django.utils.timezone import datetime

from measurements.models import RealTimeMeasurement, Tax
from measurements.serializers import (
    MinutelyMeasurementSerializer,
    MonthlyMeasurementSerializer,
    QuarterlyMeasurementSerializer,
    RealTimeMeasurementSerializer,
)
from slaves.api import request_all_events, request_measurements
from slaves.models import Slave
from transductors.models import EnergyTransductor

logger = logging.getLogger("__name__")


class DataCollector:
    def build_realtime_measurements(self, measurement):
        realtime_measurement, _ = RealTimeMeasurement.objects.get_or_create(transductor=measurement["transductor"])

        serializer = RealTimeMeasurementSerializer(realtime_measurement, data=measurement, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

    def build_minutely_measurements(self, measurement):
        serializer = MinutelyMeasurementSerializer(data=measurement)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

    def build_quarterly_measurements(self, measurement):
        measurement["tax"] = Tax.objects.last()

        serializer = QuarterlyMeasurementSerializer(data=measurement)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

    def build_monthly_measurements(self, measurement):
        serializer = MonthlyMeasurementSerializer(data=measurement)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

    def save_event_object(self, event_dict, request_type):
        """
        Builds and saves events from a dict to a given class
        """
        self.build_events(event_dict)

    def build_events(self, events):
        for event_dict in events:
            event_class = globals()[event_dict["type"]]
            transductor = EnergyTransductor.objects.get(server_address=event_dict["server_address"])
            last_event = event_class.objects.filter(transductor=transductor, ended_at__isnull=True).last()
            if last_event:
                if not event_dict["ended_at"]:
                    last_event.data = event_dict["data"]
                    last_event.save()
                else:
                    if event_dict["data"]:
                        last_event.data = event_dict["data"]

                    last_event.ended_at = event_dict["ended_at"]
                    last_event.save()
            else:
                if not event_dict["ended_at"]:
                    event_class().save_event(transductor, event_dict)

    def get_events(self):
        slave_servers = Slave.objects.all()

        for slave in slave_servers:
            event_responses = request_all_events(slave)
            for pairs in event_responses:
                loaded_events = json.loads(pairs[1].content)
                self.save_event_object(loaded_events, pairs[0])

    def get_measurements(self, measurement_type):
        if measurement_type not in MEASUREMNT_TYPES:
            raise CommandError(f"Unknown data_group: {measurement_type}")

        slaves = Slave.objects.filter(active=True, broken=False)

        for slave in slaves:
            if measurement_type == "realtime":
                self.get_realtime_measurements(slave)

            for transductor in slave.transductors.all():
                if measurement_type == "minutely":
                    self.get_minutely_measurements(slave, transductor)

                elif measurement_type == "monthly":
                    self.get_monthly_measurements(slave, transductor)

                elif measurement_type == "quarterly":
                    self.get_quarterly_measurements(slave, transductor)

    def get_realtime_measurements(self, slave):
        realtime_measurements = request_measurements("realtime-measurements", slave)

        for measurement in realtime_measurements:
            self.build_realtime_measurements(measurement)

    def get_minutely_measurements(self, slave, transductor):
        start_date = transductor.last_minutely_collection

        minutely_measurements = request_measurements("minutely-measurements", slave, transductor, start_date)

        for measurement in minutely_measurements:
            self.build_minutely_measurements(measurement)

        transductor.last_minutely_collection = timezone.now()
        transductor.save()

    def get_quarterly_measurements(self, slave, transductor):
        start_date = transductor.last_quarterly_collection

        quarterly_measurements = request_measurements("quarterly-measurements", slave, transductor, start_date)

        for measurement in quarterly_measurements:
            self.build_quarterly_measurements(measurement)

        transductor.last_quarterly_collection = timezone.now()
        transductor.save()
