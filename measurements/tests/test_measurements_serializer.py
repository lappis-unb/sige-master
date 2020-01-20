import pytest
from django.test import Client, TestCase
from django.conf import settings
from django.db import IntegrityError

from measurements.models import MinutelyMeasurement
from measurements.models import QuarterlyMeasurement
from measurements.models import MonthlyMeasurement
from measurements.serializers import ThreePhaseSerializer
from slaves.models import Slave
from transductors.models import EnergyTransductor
from datetime import datetime
import sys
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory
from django.utils import timezone
from datetime import datetime
import pytz


class MeasurementsTestCase(TestCase):
    def setUp(self):
        self.slave = Slave.objects.create(
            ip_address="1.1.1.1", location="UED FGA", broken=False
        )

        self.transductor = EnergyTransductor.objects.create(
            serial_number="12345678",
            ip_address="1.1.1.1",
            model="MD30",
            firmware_version="0.1"
        )

        self.transductor.slave_servers.add(self.slave)

        self.time = datetime(2000, 1, 1, 1, 0, 0, 0)

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

        self.factory = APIRequestFactory()

        self.request = self.factory.get("/")

        self.serializer_context = {"request": Request(self.request)}

    def test_should_get_active_power(self):
        self.assertEqual(
            self.client.get(
                '/graph/minutely_active_power/'
                '?serial_number=12345678'
                '&start_date=2000-01-01 00:00'
                '&end_date=2000-01-01 23:59'
            ).status_code,
            200)

    def test_should_three_phase_serializer(self):
        atp_serializer = ThreePhaseSerializer(
            instance=self.minutely_measurement, context=self.serializer_context
        ).data
        self.assertEqual(
            set(atp_serializer.keys()),
            set(
                [
                    "id",
                    "transductor",
                    "phase_a",
                    "phase_b",
                    "phase_c"
                ]
            ),
        )

    def test_should_not_three_phase_serializer(self):
        atp_serializer = ThreePhaseSerializer(
            instance=self.minutely_measurement, context=self.serializer_context
        ).data
        self.assertNotEqual(
            set(atp_serializer.keys()),
            set(
                [
                    "id",
                    "transductor",
                    "phase_a",
                    "phase_b",
                    "phase_c",
                    "current_a"
                ]
            ),
        )
