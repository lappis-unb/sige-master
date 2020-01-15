from django.test import TestCase
from django.utils import timezone

from slaves.models import Slave
from transductors.models import EnergyTransductor

from django.db import IntegrityError
from django.core.exceptions import ValidationError, ObjectDoesNotExist


class TestSlavesModels(TestCase):

    def setUp(self):
        self.slave = Slave.objects.create(
            ip_address="1.1.1.1",
            location="UED FGA",
            broken=False
        )

        self.slave_1 = Slave.objects.create(
            ip_address="1.1.1.2",
            location="UAC FGA",
            broken=False
        )

        self.energy_transductor = EnergyTransductor.objects.create(
            serial_number='87654321',
            ip_address='192.168.1.1',
            physical_location="MESP",
            geolocation_latitude=20.1,
            geolocation_longitude=37.9,
            name="MESP 1",
            broken=True,
            active=False,
            creation_date=timezone.now(),
            calibration_date=timezone.now(),
            firmware_version='0.1',
            model='EnergyTransductorModel'
        )

        self.slave_1.transductors.add(self.energy_transductor)

    def test_should_create_new_slave(self):
        slaves_before = len(Slave.objects.all())
        Slave.objects.create(
            ip_address="1.1.1.3",
            location="MESP FGA",
            broken=False
        )
        slaves_after = len(Slave.objects.all())

        self.assertEqual(slaves_before + 1, slaves_after)

    def test_should_read_a_existent_slave_by_ip_address(self):
        slave = Slave.objects.get(ip_address="1.1.1.1")

        self.assertEqual(slave, self.slave)

    def test_should_update_a_specific_slave(self):
        slave = Slave.objects.get(ip_address="1.1.1.1")

        original_ip_address = slave.ip_address
        original_location = slave.location
        original_broken = slave.broken

        slave.ip_address = "2.2.2.2"
        slave.location = "FAU Darcy Ribeiro"
        slave.broken = True

        slave.save()

        new_ip_address = slave.ip_address
        new_location = slave.location
        new_broken = slave.broken

        self.assertNotEqual(original_ip_address, new_ip_address)
        self.assertNotEqual(original_location, new_location)
        self.assertNotEqual(original_broken, new_broken)

    def test_should_update_a_speficic_slave_with_dns(self):
        slave = Slave.objects.get(ip_address="1.1.1.1")
        slave.ip_address = "https://api.herokuapp.com/"

        self.assertIsNone(slave.save())

    def test_should_delete_a_existent_slave(self):
        slave = Slave.objects.get(ip_address="1.1.1.1")
        self.assertTrue(slave.delete())

    def test_should_not_delete_a_inexistent_slave(self):
        with self.assertRaises(ObjectDoesNotExist):
            Slave.objects.get(ip_address="10.10.10.10").delete()

    def test_associate_transductor_to_slave_server(self):
        length = len(self.slave.transductors.all())

        self.assertIsNone(
            self.slave.transductors.add(
                self.energy_transductor
            )
        )

        self.assertEqual((length + 1), len(self.slave.transductors.all()))

    def test_remove_transductor_from_slave_server(self):
        length = len(self.slave_1.transductors.all())

        self.assertIsNone(
            self.slave_1.transductors.remove(
                self.energy_transductor
            )
        )

        self.assertEqual((length - 1), len(self.slave_1.transductors.all()))
