from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from django.utils import timezone
from measurement.models import (MinutelyMeasurement, MonthlyMeasurement,
                                QuarterlyMeasurement)
from transductor.models import EnergyTransductor
from events.models import *


class EventTestCase(TestCase):
    def setUp(self):
        self.transductor = EnergyTransductor.objects.create(
            serial_number='8764321',
            ip_address='111.101.111.11',
            broken=False,
            active=True,
            model="TR4020",
            firmware_version='12.1.3215',
            physical_location='predio 2 sala 44',
            geolocation_longitude=-24.4556,
            geolocation_latitude=-24.45996,
            installation_date=datetime.now()
        )

    def test_create_failed_connection_event(self):
        before = len(FailedConnectionEvent.objects.all())

        self.transductor.set_broken(True)
        event = FailedConnectionEvent.objects.last()

        self.assertEqual(before + 1, len(FailedConnectionEvent.objects.all()))
        self.assertEqual(self.transductor.ip_address, event.transductor_ip)

    def test_create_critical_voltage_event(self):
        before = len(CriticalVoltageEvent.objects.all())

        a = MinutelyMeasurement()
        a.voltage_a = 220
        a.voltage_b = 400
        a.voltage_c = 200
        a.check_measurements()

        b = MinutelyMeasurement()
        b.voltage_a = 220
        b.voltage_b = 110
        b.voltage_c = 200
        b.check_measurements()

        self.assertEqual(before + 2, len(CriticalVoltageEvent.objects.all()))

    def test_create_precarious_voltage_event(self):
        before = len(PrecariousVoltageEvent.objects.all())

        a = MinutelyMeasurement()
        a.voltage_a = 220
        a.voltage_b = 220
        a.voltage_c = 199
        a.check_measurements()

        b = MinutelyMeasurement()
        b.voltage_a = 220
        b.voltage_b = 230
        b.voltage_c = 220
        b.check_measurements()

        self.assertEqual(before + 2, len(PrecariousVoltageEvent.objects.all()))

    def test_create_phase_drop_event(self):
        before = len(PhaseDropEvent.objects.all())

        a = MinutelyMeasurement()
        a.voltage_a = 220
        a.voltage_b = 220
        a.voltage_c = 50
        a.check_measurements()

        self.assertEqual(before + 1, len(PhaseDropEvent.objects.all()))
