import pytest
from datetime import datetime
from django.test import TestCase
from django.conf import settings
from django.db import IntegrityError
from django.db.utils import DataError
from django.core.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist

from buildings.models import Building
from campi.models import Campus


class BuildingsTestCase(TestCase):
    def setUp(self):
        self.campus_01 = Campus.objects.create(
            name='Faculdade Gama',
            acronym='FGa',
            address="Setor Leste - Gama"
        )
        self.building_01 = Building.objects.create(
            name='pantheon',
            phone="(61) 3333-3333",
            acronym='Pan',
            campus=self.campus_01
        )

    def test_create_building(self):
        size = len(Building.objects.all())
        building = Building()
        building.name = 'ultimate building of chaos'
        building.phone = "(61) 3333-3333"
        building.acronym = 'UBC'
        building.campus = self.campus_01
        self.assertIsNone(building.save())
        self.assertEqual(size + 1, len(Building.objects.all()))

    def test_not_create_building_without_name(self):
        size = len(Building.objects.all())
        building = Building()
        building.phone = "(61) 3333-3333"
        building.acronym = 'UBC'
        building.campus = self.campus_01
        with self.assertRaises(ValidationError):
            building.save()

    def test_not_create_building_without_acronym(self):
        size = len(Building.objects.all())
        building = Building()
        building.phone = "(61) 3333-3333"
        building.name = 'UBC'
        building.campus = self.campus_01
        with self.assertRaises(ValidationError):
            building.save()

    def test_not_create_building_without_campus(self):
        size = len(Building.objects.all())

        building = Building()
        building.phone = 'Unlimited Blade Works'
        building.phone = "(61) 3333-3333"
        building.acronym = 'UBW'

        with self.assertRaises(ValidationError):
            building.save()

    def test_update_building(self):
        building = Building.objects.filter(name='pantheon')
        self.assertTrue(
            building.update(name="common house of all gods")
        )

    def test_delete_building(self):
        size = len(Building.objects.all())
        Building.objects.filter(name='pantheon').delete()
        self.assertEqual(size - 1, len(Building.objects.all()))
