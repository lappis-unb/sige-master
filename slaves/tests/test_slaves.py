from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from campi.models import Campus
from slaves.models import Slave
from transductors.models import EnergyTransductor


class TestSlavesModels(TestCase):
    def setUp(self):
        self.slave = Slave.objects.create(
            server_address="1.1.1.1",
            name="UED FGA",
            broken=False,
        )

        self.slave_1 = Slave.objects.create(
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

        # Jango Fett would be proud
        self.slave_1.transductors.add(self.energy_transductor)

    def test_should_create_new_slave(self):
        slaves_before = len(Slave.objects.all())
        Slave.objects.create(
            server_address="1.1.1.3",
            name="MESP FGA",
            broken=False,
        )
        slaves_after = len(Slave.objects.all())

        self.assertEqual(slaves_before + 1, slaves_after)

    def test_should_read_a_existent_slave_by_server_address(self):
        slave = Slave.objects.get(server_address="1.1.1.1")

        self.assertEqual(slave, self.slave)

    def test_should_update_a_specific_slave(self):
        slave = Slave.objects.get(server_address="1.1.1.1")

        original_server_address = slave.server_address
        original_name = slave.name
        original_broken = slave.broken

        slave.server_address = "2.2.2.2"
        slave.name = "FAU Darcy Ribeiro"
        slave.broken = True

        slave.save()

        new_server_address = slave.server_address
        new_name = slave.name
        new_broken = slave.broken

        self.assertNotEqual(original_server_address, new_server_address)
        self.assertNotEqual(original_name, new_name)
        self.assertNotEqual(original_broken, new_broken)

    def test_should_update_a_speficic_slave_with_dns(self):
        slave = Slave.objects.get(server_address="1.1.1.1")
        slave.server_address = "https://api.herokuapp.com/"

        self.assertIsNone(slave.save())

    def test_should_delete_a_existent_slave(self):
        slave = Slave.objects.get(server_address="1.1.1.1")
        self.assertTrue(slave.delete())

    def test_should_not_delete_a_inexistent_slave(self):
        with self.assertRaises(ObjectDoesNotExist):
            Slave.objects.get(server_address="10.10.10.10").delete()

    def test_associate_transductor_to_slave_server(self):
        length = len(self.slave.transductors.all())

        self.assertIsNone(self.slave.transductors.add(self.energy_transductor))

        self.assertEqual((length + 1), len(self.slave.transductors.all()))

    def test_remove_transductor_from_slave_server(self):
        length = len(self.slave_1.transductors.all())

        self.assertIsNone(self.slave_1.transductors.remove(self.energy_transductor))

        self.assertEqual((length - 1), len(self.slave_1.transductors.all()))
