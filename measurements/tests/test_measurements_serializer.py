import pytest
from django.test import TestCase
from django.conf import settings
from django.db import IntegrityError


from measurements.models import MinutelyMeasurement
from measurements.models import QuarterlyMeasurement
from measurements.models import MonthlyMeasurement
from measurements.serializers import MinutelyApparentPowerThreePhaseSerializer
from slaves.models import Slave
from transductors.models import EnergyTransductor
from datetime import datetime
import sys
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory
from django.utils import timezone


class MeasurementsTestCase(TestCase):
    def setUp(self):
        self.slave = Slave.objects.create(
            ip_address="1.1.1.1", location="UED FGA", broken=False
        )

        self.transductor = EnergyTransductor.objects.create(
            serial_number="12345678",
            ip_address="1.1.1.1",
            model="MD30"
        )

        self.transductor.slave_servers.add(self.slave)

        self.time = timezone.now()

        self.minutely_measurements = MinutelyMeasurement.objects.create(
            transductor=self.transductor, collection_time=self.time
        )

        self.factory = APIRequestFactory()

        self.request = self.factory.get("/")

        self.serializer_context = {"request": Request(self.request)}

    def test_should_three_phase_aparent_serializer(self):
        atp_serializer = MinutelyApparentPowerThreePhaseSerializer(
            instance=self.minutely_measurements, context=self.serializer_context
        ).data
        self.assertEqual(
            set(atp_serializer.keys()),
            set(
                [
                    "id",
                    "transductor",
                    "collection_time",
                    "apparent_power_a",
                    "apparent_power_b",
                    "apparent_power_c",
                ]
            ),
        )

    def test_should_not_three_phase_aparent_serializer(self):
        atp_serializer = MinutelyApparentPowerThreePhaseSerializer(
            instance=self.minutely_measurements, context=self.serializer_context
        ).data
        self.assertNotEqual(
            set(atp_serializer.keys()),
            set(
                [
                    "id",
                    "transductor",
                    "collection_time",
                    "apparent_power_a",
                    "apparent_power_b",
                    "apparent_power_c",
                    "current_a",
                ]
            ),
        )
