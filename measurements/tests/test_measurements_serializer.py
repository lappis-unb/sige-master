import pytest
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory
from django.test import Client, TestCase
from django.conf import settings
from django.db import IntegrityError

from measurements.serializers import MinutelyActivePowerThreePhaseSerializer
from measurements.models import MinutelyMeasurement
from slaves.models import Slave
from transductors.models import EnergyTransductor
from transductor_models.models import TransductorModel
from datetime import datetime


class MeasurementsSerializerTestCase(TestCase):
    def setUp(self):
        self.slave = Slave.objects.create(
            ip_address="1.1.1.1",
            location="UED FGA",
            broken=False
        )

        self.transductor_model = TransductorModel.objects.create(
            name="TR4020",
            serial_protocol="UDP",
            transport_protocol="modbus"
        )

        self.transductor = EnergyTransductor.objects.create(
            serial_number="12345678",
            ip_address="1.1.1.1",
            model=self.transductor_model
        )

        self.transductor.slave_servers.add(self.slave)

        self.time = datetime.now()

        self.minutely_measurements = MinutelyMeasurement.objects.create(
            transductor=self.transductor,
            collection_time=self.time
        )

    def test_should_serialize_active_power(self):
        factory = APIRequestFactory()
        request = factory.get('/')

        self.active_power = MinutelyMeasurement.objects.create(
            transductor=self.transductor,
            collection_time=datetime.now()
        )

        self.serializer = MinutelyActivePowerThreePhaseSerializer(
            instance=self.active_power,
            context={'request': Request(request)})

        self.assertEqual(
            set(self.serializer.data.keys()), 
            set(['id',
                 'transductor',
                 'collection_time',
                 'active_power_a',
                 'active_power_b',
                 'active_power_c'])
        )

    def test_should_not_serialize_active_power(self):
        factory = APIRequestFactory()
        request = factory.get('/')

        self.active_power = MinutelyMeasurement.objects.create(
            transductor=self.transductor,
            collection_time=datetime.now()
        )

        self.serializer = MinutelyActivePowerThreePhaseSerializer(
            instance=self.active_power, context={'request': Request(request)})

        self.assertNotEqual(
            set(self.serializer.data.keys()),
            set(['id',
                 'transductor',
                 'collection_date',
                 'active_power_a',
                 'active_power_b',
                 'active_power_c']))
      
    def test_should_get_active_power(self):
        self.assertEqual(
            self.client.get('/chart/minutely_active_power/').status_code,
            200)
