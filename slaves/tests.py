from django.test import TestCase
from slaves.models import Slave
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist


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

    def test_should_create_new_slave(self):
        slaves_before = len(Slave.objects.all())
        Slave.objects.create(
            ip_address="1.1.1.3",
            location="MESP FGA",
            broken=False
        )
        slaves_after = len(Slave.objects.all())

        self.assertEquals(slaves_before + 1, slaves_after)

    def test_should_not_create_same_slave(self):
        new_slave = Slave()
        new_slave.ip_address = "1.1.1.1"
        new_slave.location = "MESP FGA"
        new_slave.broken = False

        with self.assertRaises(ValidationError):
            new_slave.save()

    def test_should_read_a_existent_slave_by_ip_address(self):
        slave = Slave.objects.get(ip_address="1.1.1.1")

        self.assertEquals(slave, self.slave)

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

        self.assertNotEquals(original_ip_address, new_ip_address)
        self.assertNotEquals(original_location, new_location)
        self.assertNotEquals(original_broken, new_broken)

    def test_should_not_update_a_speficic_slave_with_wrong_ip_address(self):
        slave = Slave.objects.get(ip_address="1.1.1.1")
        slave.ip_address = "some ip adreess"

        with self.assertRaises(ValidationError):
            slave.save()

    def test_should_delete_a_existent_slave(self):
        slave = Slave.objects.get(ip_address="1.1.1.1")
        self.assertTrue(slave.delete())

    def test_should_not_delete_a_inexistent_slave(self):
        with self.assertRaises(ObjectDoesNotExist):
            Slave.objects.get(ip_address="10.10.10.10").delete()
