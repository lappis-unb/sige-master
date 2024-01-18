import pytz
from django.test import TestCase
from rest_framework.exceptions import NotAcceptable
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from campi.models import Campus
from campi.serializers import CampusSerializer
from groups.models import Group, GroupType
from groups.serializers import GroupSerializer
from transductors.models import EnergyTransductor
from transductors.serializers import EnergyTransductorSerializer
from transductors.views import EnergyTransductorViewSet


class GroupTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

        self.request = self.factory.get("/")

        self.serializer_context = {"request": Request(self.request)}

        self.campus = Campus.objects.create(name="UnB - Faculdade Gama", acronym="FGA")

        self.serializer_campus = CampusSerializer(instance=self.campus, context=self.serializer_context).data

        self.building_type = GroupType.objects.create(name="Prédio")

        self.another_building_type = GroupType.objects.create(name="Departamento")

        self.group = Group.objects.create(name="FT", type=self.another_building_type)

        self.serializer_group = GroupSerializer(instance=self.group, context=self.serializer_context).data

        self.another_group = Group.objects.create(name="UED", type=self.another_building_type)

        self.serializer_another_group = GroupSerializer(
            instance=self.another_group, context=self.serializer_context
        ).data

        self.other_group = Group.objects.create(name="UAC", type=self.building_type)

        self.serializer_other_group = GroupSerializer(instance=self.other_group, context=self.serializer_context).data

        self.view_list = EnergyTransductorViewSet.as_view(
            {"post": "create", "get": "list", "put": "update", "patch": "partial_update", "delete": "destroy"}
        )

    def test_not_create_transductor_wrong_compus_id(self):
        params = {
            "serial_number": "8293010",
            "ip_address": "172.24.0.3",
            "port": 65535,
            "geolocation_latitude": -48.04542,
            "geolocation_longitude": -15.989753,
            "firmware_version": "0.3",
            "name": "ICC Sul",
            "broken": True,
            "active": False,
            "campus": 1,
            "model": "TR4020",
            "grouping": [1],
            "history": "Transductor history",
        }

        request = self.factory.post("energy-transductors", params)
        response = self.view_list(request)

        self.assertEqual(response.status_code, 400)

    def test_update_transductor_with_more_than_one_group(self):
        params = {
            "serial_number": "8293010",
            "ip_address": "172.24.0.3",
            "port": 65535,
            "geolocation_latitude": -48.04542,
            "geolocation_longitude": -15.989753,
            "firmware_version": "0.3",
            "name": "ICC Sul",
            "broken": True,
            "active": False,
            "campus": self.serializer_campus["id"],
            "model": "TR4020",
            "grouping": [self.serializer_group["id"], self.serializer_other_group["id"]],
            "history": "Transductor history",
        }

        request = self.factory.post("energy-transductors", params)
        response = self.view_list(request)

        self.assertEqual(response.status_code, 201)
