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

        self.transductor_model = TransductorModel()
        self.transductor_model.model_code = "987654321"
        self.transductor_model.name = "TR4020"
        self.transductor_model.serial_protocol = "UDP"
        self.transductor_model.transport_protocol = "modbus"
        self.transductor_model.minutely_register_addresses = [[1, 1]]
        self.transductor_model.quarterly_register_addresses = [[1, 1]]
        self.transductor_model.monthly_register_addresses = [[1, 1]]
        self.transductor_model.save(bypass_requests=True)

        self.transductor = EnergyTransductor.objects.create(
            serial_number="12345678",
            ip_address="1.1.1.1",
            model=self.transductor_model,
        )

        self.transductor.slave_servers.add(self.slave)

        self.time = datetime.now()

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
            self.client.get('/graph/minutely_active_power/').status_code,
            200)
