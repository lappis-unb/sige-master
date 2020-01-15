import pytest
from django.test import TestCase
from django.conf import settings
from django.db import IntegrityError

from measurements.models import MinutelyMeasurement
from measurements.models import QuarterlyMeasurement
from measurements.models import MonthlyMeasurement
from slaves.models import Slave
from transductors.models import EnergyTransductor
from datetime import datetime
from django.utils import timezone


class MeasurementsTestCase(TestCase):

    def setUp(self):
        self.slave = Slave.objects.create(
            ip_address="1.1.1.1",
            location="UED FGA",
            broken=False
        )

        self.transductor = EnergyTransductor.objects.create(
            serial_number="12345678",
            ip_address="1.1.1.1",
            model='EnergyTransductorModel',
            firmware_version="0.1"
        )

        self.transductor.slave_servers.add(self.slave)

        self.time = timezone.now()

        self.minutely_measurement = MinutelyMeasurement.objects.create(
            frequency_a=8,
            voltage_a=8,
            voltage_b=8,
            voltage_c=8,
            current_a=8,
            current_b=8,
            current_c=8,
            active_power_a=8,
            active_power_b=8,
            active_power_c=8,
            total_active_power=8,
            reactive_power_a=8,
            reactive_power_b=8,
            reactive_power_c=8,
            total_reactive_power=8,
            apparent_power_a=8,
            apparent_power_b=8,
            apparent_power_c=8,
            total_apparent_power=8,
            power_factor_a=8,
            power_factor_b=8,
            power_factor_c=8,
            total_power_factor=8,
            dht_voltage_a=8,
            dht_voltage_b=8,
            dht_voltage_c=8,
            dht_current_a=8,
            dht_current_b=8,
            dht_current_c=8,
            transductor=self.transductor,
            collection_time=self.time
        )

        self.quarterly_measurement = QuarterlyMeasurement.objects.create(
            generated_energy_peak_time=8,
            generated_energy_off_peak_time=8,
            consumption_peak_time=8,
            consumption_off_peak_time=8,
            inductive_power_peak_time=8,
            inductive_power_off_peak_time=8,
            capacitive_power_peak_time=8,
            capacitive_power_off_peak_time=8,
            transductor=self.transductor,
            collection_time=self.time
        )

        self.monthly_measurement = MonthlyMeasurement.objects.create(
            generated_energy_peak_time=8,
            generated_energy_off_peak_time=8,
            consumption_peak_time=8,
            consumption_off_peak_time=8,
            inductive_power_peak_time=8,
            inductive_power_off_peak_time=8,
            capacitive_power_peak_time=8,
            capacitive_power_off_peak_time=8,
            active_max_power_peak_time=8,
            active_max_power_off_peak_time=8,
            reactive_max_power_peak_time=8,
            reactive_max_power_off_peak_time=8,
            active_max_power_list_peak_time=[
                {"value": 0.0, "timestamp": "2019-02-05 14:00:00"},
                {"value": 0.0, "timestamp": "2019-02-05 14:00:00"},
                {"value": 0.0, "timestamp": "2019-02-05 14:00:00"},
                {"value": 0.0, "timestamp": "2019-02-05 14:00:00"}
            ],
            active_max_power_list_off_peak_time=[
                {"value": 0.0, "timestamp": "2019-02-05 14:00:00"},
                {"value": 0.0, "timestamp": "2019-02-05 14:00:00"},
                {"value": 0.0, "timestamp": "2019-02-05 14:00:00"},
                {"value": 0.0, "timestamp": "2019-02-05 14:00:00"}
            ],
            reactive_max_power_list_peak_time=[
                {"value": 0.0, "timestamp": "2019-02-05 14:00:00"},
                {"value": 0.0, "timestamp": "2019-02-05 14:00:00"},
                {"value": 0.0, "timestamp": "2019-02-05 14:00:00"},
                {"value": 0.0, "timestamp": "2019-02-05 14:00:00"}
            ],
            reactive_max_power_list_off_peak_time=[
                {"value": 0.0, "timestamp": "2019-02-05 14:00:00"},
                {"value": 0.0, "timestamp": "2019-02-05 14:00:00"},
                {"value": 0.0, "timestamp": "2019-02-05 14:00:00"},
                {"value": 0.0, "timestamp": "2019-02-05 14:00:00"}
            ],
            transductor=self.transductor,
            collection_time=self.time
        )

    # Minutely measurements tests

    def test_create_new_minutely_measurement(self):
        before = len(MinutelyMeasurement.objects.all())
        MinutelyMeasurement.objects.create(
            frequency_a=8,
            voltage_a=8,
            voltage_b=8,
            voltage_c=8,
            current_a=8,
            current_b=8,
            current_c=8,
            active_power_a=8,
            active_power_b=8,
            active_power_c=8,
            total_active_power=8,
            reactive_power_a=8,
            reactive_power_b=8,
            reactive_power_c=8,
            total_reactive_power=8,
            apparent_power_a=8,
            apparent_power_b=8,
            apparent_power_c=8,
            total_apparent_power=8,
            power_factor_a=8,
            power_factor_b=8,
            power_factor_c=8,
            total_power_factor=8,
            dht_voltage_a=8,
            dht_voltage_b=8,
            dht_voltage_c=8,
            dht_current_a=8,
            dht_current_b=8,
            dht_current_c=8,
            transductor=self.transductor,
            collection_time=timezone.now()
        )
        after = len(MinutelyMeasurement.objects.all())

        self.assertEqual(before + 1, after)

    def test_should_not_create_minutely_measurement_without_collection_time(
            self):
        new_measurement = MinutelyMeasurement()
        new_measurement.transductor = self.transductor

        with self.assertRaises(IntegrityError):
            new_measurement.save()

    def test_should_not_create_minutely_measurement_without_transductor(self):
        new_measurement = MinutelyMeasurement()
        new_measurement.collection_time = timezone.now()

        with self.assertRaises(IntegrityError):
            new_measurement.save()

    def test_delete_a_existent_minutely_measurement(self):
        measurements = MinutelyMeasurement.objects.last()
        self.assertTrue(measurements.delete())

    # Quarterly measurements tests
    def test_create_new_quarterly_measurement(self):
        before = len(QuarterlyMeasurement.objects.all())
        QuarterlyMeasurement.objects.create(
            generated_energy_peak_time=8,
            generated_energy_off_peak_time=8,
            consumption_peak_time=8,
            consumption_off_peak_time=8,
            inductive_power_peak_time=8,
            inductive_power_off_peak_time=8,
            capacitive_power_peak_time=8,
            capacitive_power_off_peak_time=8,
            transductor=self.transductor,
            collection_time=timezone.now()
        )
        after = len(QuarterlyMeasurement.objects.all())

        self.assertEqual(before + 1, after)

    def test_should_not_create_quarterly_measurement_without_collection_time(
            self):
        new_measurement = QuarterlyMeasurement()
        new_measurement.transductor = self.transductor

        with self.assertRaises(IntegrityError):
            new_measurement.save()

    def test_should_not_create_quarterly_measurement_without_transductor(self):
        new_measurement = QuarterlyMeasurement()
        new_measurement.collection_time = timezone.now()

        with self.assertRaises(IntegrityError):
            new_measurement.save()

    def test_delete_a_existent_quarterly_measurement(self):
        measurements = QuarterlyMeasurement.objects.last()
        self.assertTrue(measurements.delete())

    # Monthly measurements tests
    def test_create_new_monthly_measurement(self):
        before = len(MonthlyMeasurement.objects.all())
        MonthlyMeasurement.objects.create(
            generated_energy_peak_time=8,
            generated_energy_off_peak_time=8,
            consumption_peak_time=8,
            consumption_off_peak_time=8,
            inductive_power_peak_time=8,
            inductive_power_off_peak_time=8,
            capacitive_power_peak_time=8,
            capacitive_power_off_peak_time=8,
            active_max_power_peak_time=8,
            active_max_power_off_peak_time=8,
            reactive_max_power_peak_time=8,
            reactive_max_power_off_peak_time=8,
            active_max_power_list_peak_time=[
                {"value": 0.0, "timestamp": "2019-02-05 14:00:00"},
                {"value": 0.0, "timestamp": "2019-02-05 14:00:00"},
                {"value": 0.0, "timestamp": "2019-02-05 14:00:00"},
                {"value": 0.0, "timestamp": "2019-02-05 14:00:00"}
            ],
            active_max_power_list_off_peak_time=[
                {"value": 0.0, "timestamp": "2019-02-05 14:00:00"},
                {"value": 0.0, "timestamp": "2019-02-05 14:00:00"},
                {"value": 0.0, "timestamp": "2019-02-05 14:00:00"},
                {"value": 0.0, "timestamp": "2019-02-05 14:00:00"}
            ],
            reactive_max_power_list_peak_time=[
                {"value": 0.0, "timestamp": "2019-02-05 14:00:00"},
                {"value": 0.0, "timestamp": "2019-02-05 14:00:00"},
                {"value": 0.0, "timestamp": "2019-02-05 14:00:00"},
                {"value": 0.0, "timestamp": "2019-02-05 14:00:00"}
            ],
            reactive_max_power_list_off_peak_time=[
                {"value": 0.0, "timestamp": "2019-02-05 14:00:00"},
                {"value": 0.0, "timestamp": "2019-02-05 14:00:00"},
                {"value": 0.0, "timestamp": "2019-02-05 14:00:00"},
                {"value": 0.0, "timestamp": "2019-02-05 14:00:00"}
            ],
            transductor=self.transductor,
            collection_time=timezone.now()
        )
        after = len(MonthlyMeasurement.objects.all())

        self.assertEqual(before + 1, after)

    def test_should_not_create_monthly_measurement_without_collection_time(
            self):
        new_measurement = MonthlyMeasurement()
        new_measurement.transductor = self.transductor

        with self.assertRaises(IntegrityError):
            new_measurement.save()

    def test_should_not_create_monthly_measurement_without_transductor(self):
        new_measurement = MonthlyMeasurement()
        new_measurement.collection_time = timezone.now()

        with self.assertRaises(IntegrityError):
            new_measurement.save()

    def test_delete_a_existent_monthly_measurement(self):
        measurements = MonthlyMeasurement.objects.last()
        self.assertTrue(measurements.delete())
