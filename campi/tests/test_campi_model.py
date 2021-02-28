from django.test import TestCase
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist

from ..models import Campus


class CampiTestCase(TestCase):

    def setUp(self):
        self.campus = Campus.objects.create(
            name="Campus da Faculdade Gama",
            acronym="FGA",
        )

        self.campus_1 = Campus.objects.create(
            name="Campus de Planaltina",
            acronym="FUP",
        )

    def test_create_new_campus(self):
        campi_before = len(Campus.objects.all())
        Campus.objects.create(
            name="Campus da Faculdade de Ceilândia",
            acronym="FCE",
        )
        campi_after = len(Campus.objects.all())

        self.assertEqual(campi_before + 1, campi_after)

    def test_should_not_create_same_campus(self):
        new_campus = Campus()
        new_campus.name = "Campus da Faculdade Gama"
        new_campus.acronym = "FGA"

        with self.assertRaises(ValidationError):
            new_campus.save()

    def test_should_not_create_without_name(self):
        new_campus = Campus()
        new_campus.acronym = "FGa"

        with self.assertRaises(ValidationError):
            new_campus.save()

    def test_should_not_create_without_acronym(self):
        new_campus = Campus()
        new_campus.name = "Facul Gama"

        with self.assertRaises(ValidationError):
            new_campus.save()

    def test_read_a_existent_campus_by_acronym(self):
        campus = Campus.objects.get(acronym="FGA")

        self.assertEqual(campus, self.campus)

    def test_read_a_existent_campus_by_name(self):
        campus = Campus.objects.get(name="Campus da Faculdade Gama")

        self.assertEqual(campus, self.campus)

    def test_update_a_specific_campus(self):
        campus = Campus.objects.get(acronym="FGA")

        original_name = campus.name
        original_acronym = campus.acronym

        campus.name = "Faculdade Ceilândia"
        campus.acronym = "FCE"
        campus.save()

        new_name = campus.name
        new_acronym = campus.acronym

        self.assertNotEqual(original_name, new_name)
        self.assertNotEqual(original_acronym, new_acronym)

    def test_not_update_a_speficic_campus(self):
        campus = Campus.objects.get(acronym="FUP")
        campus.acronym = "FGA"

        with self.assertRaises(IntegrityError):
            campus.save_base()

    def test_delete_a_existent_campus(self):
        campus = Campus.objects.get(acronym="FGA")
        self.assertTrue(campus.delete())

    def test_try_delete_a_inexistent_campus(self):
        with self.assertRaises(ObjectDoesNotExist):
            Campus.objects.get(acronym="FCE").delete()
