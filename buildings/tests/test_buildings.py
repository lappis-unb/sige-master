import pytest
from datetime import datetime
from django.test import TestCase
from django.conf import settings
from django.db import IntegrityError
from django.db.utils import DataError
from django.core.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist

from buildings.models import Building


class BuildingsTestCase(TestCase):
    def setUp(self):
        building_01 = Building.objects.create(
            name='pantheon',
            phone='55555555555',
            acronym='Pan'
        )

    def test_create_building(self):
        size = len(Building.objects.all())
        building = Building()
        building.name = 'ultimate building of chaos'
        building.phone = '00000000000'
        building.acronym = 'UBC'
        self.assertIsNone(building.save())
        self.assertEqual(size + 1, len(Building.objects.all()))

    def test_not_create_building_without_name(self):
        size = len(Building.objects.all())
        building = Building()
        building.phone = '00000000000'
        building.acronym = 'UBC'
        with self.assertRaises(ValidationError):
            a = building.save()

    def test_not_create_building_without_acronym(self):
        size = len(Building.objects.all())
        building = Building()
        building.phone = '00000000000'
        building.name = 'UBC'
        with self.assertRaises(ValidationError):
            a = building.save()

    # for when making relationships with other models
    # def test_not_create_building_without_rel(self):
    #     size = len(Building.objects.all())

    #     building = Building()
    #     building.phone = 'Unlimited Blade Works'
    #     building.phone = '00000000000'
    #     building.acronym = 'UBW'

    #     with self.assertRaises(DataError):
    #         building.save()

    def test_update_building(self):
        building = Building.objects.filter(name='pantheon')
        self.assertTrue(
            building.update(name="common house of all gods")
        )

    def test_delete_building(self):
        size = len(Building.objects.all())
        Building.objects.filter(name='pantheon').delete()
        self.assertEqual(size - 1, len(Building.objects.all()))
