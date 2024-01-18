from django.test import TestCase
from unittest import TestCase
from django.utils import timezone
from campi.models import Campus
from slaves.models import Slave
from transductors.models import EnergyTransductor
from events.models import FailedConnectionSlaveEvent
from django.utils.deprecation import RemovedInDjango40Warning
import warnings

class TestSlavesModels(TestCase):
    def setUp(self):
        warnings.simplefilter("ignore", category=RemovedInDjango40Warning)
        self.broken_slave = Slave.objects.create(
            server_address="1.1.1.1",
            name="UED FGA",
            broken=True,
        )
        self.unbroken_slave = Slave.objects.create(
            server_address="1.1.1.1",
            name="UED FGA",
            broken=True,
        )
        self.slave_with_transductor = Slave.objects.create(
            server_address="1.1.1.2",
            name="UAC FGA",
            broken=False,
        )
        self.campus = Campus.objects.create(
            name="UnB - Faculdade Gama",
            acronym="FGA",
        )
        self.energy_transductor = EnergyTransductor.objects.create(
            serial_number="87654321",
            ip_address="192.168.1.1",
            geolocation_latitude=20.1,
            geolocation_longitude=37.9,
            name="MESP 1",
            broken=True,
            active=False,
            creation_date=timezone.now(),
            firmware_version="0.1",
            model="EnergyTransductorModel",
            campus=self.campus,
        )
        self.slave_1.transductors.add(self.energy_transductor)
    
    # ALL tests shall be written as
    # Setup of desired situation + assertions

    # First Condition tests
    # Broken Slave

    def test_first_condition_with_false_new_status(self):
        slave_test = self.broken_slave
        related_events_before = len(FailedConnectionSlaveEvent.objects.all())
        slave_test.set_broken(self, False)
        related_events_now = len(FailedConnectionSlaveEvent.objects.all())

        self.assertEqual(slave_test.broken, False)
        self.assertEqual(related_events_before + 1, related_events_now)

    def test_first_condition_with_true_new_status(self):
        slave_test = self.broken_slave
        slave_broken_before = slave_test.broken
        related_events_before = len(FailedConnectionSlaveEvent.objects.all())
        slave_test.set_broken(self, True)
        slave_broken_after = slave_test.broken
        related_events_now = len(FailedConnectionSlaveEvent.objects.all())

        self.assertEqual(slave_broken_before, slave_broken_after)
        self.assertEqual(related_events_before, related_events_now)

    # Unbroken Slave
    def test_first_condition_with_false_new_and_old_status(self):
        slave_test = self.unbroken_slave
        slave_broken_before = slave_test.broken
        related_events_before = len(FailedConnectionSlaveEvent.objects.all())
        slave_test.set_broken(self, False)
        slave_broken_after = slave_test.broken
        related_events_now = len(FailedConnectionSlaveEvent.objects.all())

        self.assertEqual(slave_broken_before, slave_broken_after)
        self.assertEqual(related_events_before, related_events_now)
    
    # Second Condition tests
    # Unbroken Slave
    def test_second_condition_with_true_new_status(self):
        slave_test = self.unbroken_slave
        related_events_before = len(FailedConnectionSlaveEvent.objects.all())
        slave_test.set_broken(self, True)
        related_events_now = len(FailedConnectionSlaveEvent.objects.all())

        self.assertEqual(slave_test.broken, True)
        self.assertEqual(related_events_before + 1, related_events_now)

    def test_second_condition_with_false_new_status(self):
        slave_test = self.unbroken_slave
        slave_broken_before = slave_test.broken
        related_events_before = len(FailedConnectionSlaveEvent.objects.all())
        slave_test.set_broken(self, False)
        slave_broken_after = slave_test.broken
        related_events_now = len(FailedConnectionSlaveEvent.objects.all())

        self.assertEqual(slave_broken_before, slave_broken_after)
        self.assertEqual(related_events_before, related_events_now)

    # Broken Slave
    def test_second_condition_with_true_new_and_old_status(self):
        slave_test = self.broken_slave
        slave_broken_before = slave_test.broken
        related_events_before = len(FailedConnectionSlaveEvent.objects.all())
        slave_test.set_broken(self, True)
        slave_broken_after = slave_test.broken
        related_events_now = len(FailedConnectionSlaveEvent.objects.all())

        self.assertEqual(slave_broken_before, slave_broken_after)
        self.assertEqual(related_events_before, related_events_now)