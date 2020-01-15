from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from django.utils import timezone

from events.models import *

from transductors.models import EnergyTransductor

from slaves.models import Slave

from measurements.models import MonthlyMeasurement
from measurements.models import MinutelyMeasurement
from measurements.models import QuarterlyMeasurement


class EventTestCase(TestCase):
    def setUp(self):
        self.transductor = EnergyTransductor.objects.create(
            serial_number='8764321',
            ip_address='111.101.111.11',
            broken=False,
            active=True,
            model='TR4020',
            location='predio 2 sala 44',
            longitude=-24.4556,
            latitude=-24.45996
        )

        self.slave = Slave.objects.create(
            ip_address='666.666.666.666',
            port=80,
            location='somewhere near Vïsklav - Czech Repuplic',
            broken=False
        )

    def test_create_failed_connection_with_slave_event(self):
        before = len(FailedConnectionSlaveEvent.objects.all())

        self.slave.set_broken(True)
        event = FailedConnectionSlaveEvent.objects.last()

        self.assertEqual(before + 1, len(FailedConnectionSlaveEvent.objects.all()))
        self.assertEqual(self.slave.ip_address, event.slave.ip_address)

    def test_connection_with_slave_endpoint_for__event(self):
        pass

    def test_connection_with_slave_endpoint_for_transductor_comms_event(self):
        pass

    def test_connection_with_slave_endpoint_for_voltage_event(self):
        pass
