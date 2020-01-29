import pytest
from django.test import TestCase

from transductors.models import EnergyTransductor
from campi.models import Campus
from groups.models import Group
from groups.models import GroupType
from transductors.serializers import EnergyTransductorSerializer
from groups.serializers import GroupSerializer
from campi.serializers import CampusSerializer
from rest_framework.exceptions import NotAcceptable
from transductors.views import EnergyTransductorViewSet

from rest_framework.request import Request
from rest_framework.test import APIRequestFactory
import pytz


class MeasurementsTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

        self.request = self.factory.get("/")

        self.serializer_context = {"request": Request(self.request)}

        self.campus = Campus.objects.create(
            name='UnB - Faculdade Gama',
            acronym='FGA',
            phone='(61) 3107-8901',
            address='Área Especial de Indústria Projeção A',
            website_address='http://fga.unb.br/'
        )

        self.serializer_campus = CampusSerializer(
            instance=self.campus,
            context=self.serializer_context
        ).data

        self.building_type = GroupType.objects.create(
            name='Prédio'
        )

        self.another_building_type = GroupType.objects.create(
            name='Departamento'
        )

        self.group = Group.objects.create(
            name='FT',
            type=self.another_building_type
        )

        self.serializer_group = GroupSerializer(
            instance=self.group,
            context=self.serializer_context
        ).data

        self.another_group = Group.objects.create(
            name='UED',
            type=self.another_building_type
        )

        self.serializer_another_group = GroupSerializer(
            instance=self.another_group,
            context=self.serializer_context
        ).data

        self.other_group = Group.objects.create(
            name='UAC',
            type=self.building_type
        )

        self.serializer_other_group = GroupSerializer(
            instance=self.other_group,
            context=self.serializer_context
        ).data

        self.view_list = EnergyTransductorViewSet.as_view(
            {
                'post': 'create',
                'get': 'list',
                'put': 'update',
                'patch': 'partial_update',
                'delete': 'destroy'
            }
        )

    def test_not_create_transductor_with_same_group_type(self):
        params = {
            'serial_number': '8293010',
            'ip_address': '172.24.0.3',
            'physical_location': 'ICC Sul',
            'geolocation_latitude': -48.04542,
            'geolocation_longitude': -15.989753,
            'firmware_version': '0.3',
            'name': 'Medidor A',
            'broken': True,
            'active': False,
            'campus': self.serializer_campus['url'],
            'model': 'TR4020',
            'grouping': [
                self.serializer_group['url'],
                self.serializer_another_group['url']
            ]
        }

        request = self.factory.post('energy-transductors', params)
        response = self.view_list(request)

        self.assertEqual(response.status_code, 406)

    def test_update_transductor_with_more_than_one_group(self):
        params = {
            'serial_number': '8293010',
            'ip_address': '172.24.0.3',
            'physical_location': 'ICC Sul',
            'geolocation_latitude': -48.04542,
            'geolocation_longitude': -15.989753,
            'firmware_version': '0.3',
            'name': 'Medidor A',
            'broken': True,
            'active': False,
            'campus': self.serializer_campus['url'],
            'model': 'TR4020',
            'grouping': [
                self.serializer_group['url'],
                self.serializer_other_group['url']
            ]
        }

        request = self.factory.post('energy-transductors', params)
        response = self.view_list(request)

        self.assertEqual(response.status_code, 201)
