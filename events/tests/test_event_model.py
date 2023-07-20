from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from django.utils import timezone

from campi.models import Campus
from events.models import *
from measurements.models import (
    MinutelyMeasurement,
    MonthlyMeasurement,
    QuarterlyMeasurement,
)
from slaves.models import Slave
from transductors.models import EnergyTransductor


class EventTestCase(TestCase):
    def setUp(self):
        self.campus = Campus.objects.create(
            name="UnB - Faculdade Gama",
            acronym="FGA",
        )

        self.transductor = EnergyTransductor.objects.create(
            serial_number="8764321",
            server_address="111.101.111.11",
            broken=False,
            active=True,
            model="TR4020",
            geolocation_longitude=-24.4556,
            geolocation_latitude=-24.45996,
            firmware_version="0.1",
            campus=self.campus,
        )

        self.slave = Slave.objects.create(
            server_address="666.666.666.666", port=80, name="Somewhere near Wkïskh - Czech Republic", broken=False
        )

    def test_create_failed_connection_with_slave_event(self):
        before = len(FailedConnectionSlaveEvent.objects.all())

        self.slave.set_broken(True)
        event = FailedConnectionSlaveEvent.objects.last()

        self.assertEqual(before + 1, len(FailedConnectionSlaveEvent.objects.all()))
        self.assertEqual(self.slave.server_address, event.slave.server_address)
