import pytest
from django.test import TestCase
from django.conf import settings
from django.db import IntegrityError


from measurements.models import MinutelyMeasurement
from measurements.models import QuarterlyMeasurement
from measurements.models import MonthlyMeasurement
from measurements.serializers import ThreePhaseSerializer
from slaves.models import Slave
from transductors.models import EnergyTransductor
from transductor_models.models import TransductorModel
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

        self.transductor_model = TransductorModel.objects.create(
            model_code='987654321', name="TR4020",
            serial_protocol="UDP", transport_protocol="modbus",
            minutely_register_addresses=[[1, 1]],
            quarterly_register_addresses=[[1, 1]],
            monthly_register_addresses=[[1, 1]]
        )

        self.transductor = EnergyTransductor.objects.create(
            serial_number="12345678",
            ip_address="1.1.1.1",
            model=self.transductor_model
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
        atp_serializer = ThreePhaseSerializer(
            instance=self.minutely_measurements, context=self.serializer_context
        ).data
        self.assertEqual(
            set(atp_serializer.keys()),
            set(
                [
                    "id",
                    "transductor",
                    "collection_time",
                    "phase_a",
                    "phase_b",
                    "phase_c",
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
                    "phase_a",
                    "phase_b",
                    "phase_c",
                    "current_a",
                ]
            ),
        )
