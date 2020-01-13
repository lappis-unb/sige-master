import pytest
from django.utils import timezone
from django.test import TestCase
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError

from slaves.models import Slave
from transductors.models import Transductor, EnergyTransductor


class TransductorTestCase(TestCase):
    def setUp(self):
        self.sample_energy_transductor = EnergyTransductor.objects.create(
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

        self.sample_slave_server = Slave.objects.create(
            ip_address="10.0.0.1",
            location="FGA",
            broken=False
        )

    def test_create_transductor(self):
        size = len(EnergyTransductor.objects.all())

        transductor = EnergyTransductor.objects.create(
            serial_number='12345678',
            ip_address='192.168.10.10',
            physical_location="MESP",
            geolocation_latitude=20.1,
            geolocation_longitude=37.9,
            name="MESP 2",
            broken=False,
            active=True,
            creation_date=timezone.now(),
            calibration_date=timezone.now(),
            firmware_version='0.1',
            model='EnergyTransductorModel'
        )

        self.assertIs(
            EnergyTransductor,
            transductor.__class__
        )
        self.assertEqual(size + 1, len(EnergyTransductor.objects.all()))

    def test_not_create_transductor_with_existent_serial_number(self):
        size = len(EnergyTransductor.objects.all())

        with self.assertRaises(ValidationError):
            transductor = EnergyTransductor.objects.create(
                serial_number='87654321',
                ip_address='192.168.10.10',
                physical_location="MESP",
                geolocation_latitude=20.1,
                geolocation_longitude=37.9,
                name="MESP 2",
                broken=False,
                active=True,
                creation_date=timezone.now(),
                calibration_date=timezone.now(),
                firmware_version='0.1',
                model='EnergyTransductorModel'
            )

        self.assertEqual(size, len(EnergyTransductor.objects.all()))

    def test_not_create_transductor_with_no_serial_number(self):
        size = len(EnergyTransductor.objects.all())

        with self.assertRaises(ValidationError):
            transductor = EnergyTransductor.objects.create(
                ip_address='192.168.10.10',
                physical_location="MESP",
                geolocation_latitude=20.1,
                geolocation_longitude=37.9,
                name="MESP 2",
                broken=False,
                active=True,
                creation_date=timezone.now(),
                calibration_date=timezone.now(),
                firmware_version='0.1',
                model='EnergyTransductorModel'
            )

        self.assertEqual(size, len(EnergyTransductor.objects.all()))

    def test_not_create_transductor_with_no_transductor_model(self):
        size = len(EnergyTransductor.objects.all())

        with self.assertRaises(ValidationError):
            transductor = EnergyTransductor.objects.create(
                serial_number='87554321',
                ip_address='192.168.10.10',
                physical_location="MESP",
                geolocation_latitude=20.1,
                geolocation_longitude=37.9,
                name="MESP 2",
                broken=False,
                active=True,
                creation_date=timezone.now(),
                firmware_version='0.1',
                calibration_date=timezone.now()
            )

        self.assertEqual(size, len(EnergyTransductor.objects.all()))

    def test_update_transductor_single_field(self):
        transductor = EnergyTransductor.objects.filter(serial_number='87654321')
        self.assertTrue(
            transductor.update(
                name='UAC'
            )
        )

    def test_update_all_transductor_fields(self):
        transductor = EnergyTransductor.objects.filter(serial_number='87654321')
        self.assertTrue(
            transductor.update(
                serial_number='88888888',
                ip_address='192.168.10.12',
                physical_location="UED",
                geolocation_latitude=20.2,
                geolocation_longitude=37.0,
                name="UED 1",
                broken=True,
                active=False,
                creation_date=timezone.now(),
                firmware_version='0.1',
                calibration_date=timezone.now()
            )
        )

    def test_not_update_transductor_with_existent_serial_number(self):
        EnergyTransductor.objects.create(
            serial_number='12345678',
            ip_address='192.168.10.10',
            physical_location="MESP",
            geolocation_latitude=20.1,
            geolocation_longitude=37.9,
            name="MESP 2",
            broken=False,
            active=True,
            creation_date=timezone.now(),
            calibration_date=timezone.now(),
            firmware_version='0.1',
            model='EnergyTransductorModel'
        )

        transductor = EnergyTransductor.objects.filter(serial_number='87654321')

        with self.assertRaises(IntegrityError):
            transductor.update(
                serial_number='12345678',
                ip_address='192.168.10.12',
                physical_location="UED",
                geolocation_latitude=20.2,
                geolocation_longitude=37.0,
                name="UED 1",
                broken=True,
                active=False,
                creation_date=timezone.now(),
                firmware_version='0.1',
                calibration_date=timezone.now()
            )

    def test_retrieve_one_transductors(self):
        transductor = EnergyTransductor.objects.get(serial_number='87654321')

        self.assertIs(EnergyTransductor, transductor.__class__)

    def test_delete_transductor(self):
        transductor = EnergyTransductor.objects.filter(serial_number='87654321')

        self.assertTrue(
            transductor.delete()
        )

    def test_not_activate_transductor_with_no_slave_server_associated(self):
        self.assertFalse(
            self.sample_energy_transductor.get_active_status()
        )

    def test_should_activate_transductor_associated_with_slave_server(self):
        self.assertIsNone(
            self.sample_energy_transductor.slave_servers.add(
                self.sample_slave_server
            )
        )

        self.assertTrue(
            self.sample_energy_transductor.get_active_status()
        )
