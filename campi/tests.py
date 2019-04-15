from django.test import TestCase
from campi.models import Campus
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist


class TestCampiModels(TestCase):

    def setUp(self):
        self.campus = Campus.objects.create(
            name="Campus da Faculdade Gama",
            acronym="FGA",
            phone="(61) 3333-3333",
            address="Setor Leste - Gama",
            website_address="https://fga.unb.br/"
        )

        self.campus_1 = Campus.objects.create(
            name="Campus de Planaltina",
            acronym="FUP",
            phone="(61) 3737-3737",
            address="Planaltina",
            website_address="https://fup.unb.br/"
        )

    def test_create_new_campus(self):
        campi_before = len(Campus.objects.all())
        Campus.objects.create(
            name="Campus da Faculdade de Ceilândia",
            acronym="FCE",
            phone="(61) 3333-3333",
            address="Perto do metrô",
            website_address="https://fga.unb.br/"
        )
        campi_after = len(Campus.objects.all())

        self.assertEquals(campi_before + 1, campi_after)

    def test_should_not_create_same_campus(self):
        new_campus = Campus()
        new_campus.name = "Campus da Faculdade Gama"
        new_campus.acronym = "FGA"
        new_campus.phone = "(61) 3333-3333"
        new_campus.address = "Setor Leste - Gama"
        new_campus.website_address = "https://fga.unb.br/"

        with self.assertRaises(ValidationError):
            new_campus.save()

    def test_should_not_create_without_name(self):
        new_campus = Campus()
        new_campus.acronym = "FGa"
        new_campus.phone = "(61) 3333-3333"
        new_campus.address = "Setor Leste"
        new_campus.website_address = "https://fga.unb.br/"

        with self.assertRaises(ValidationError):
            new_campus.save()

    def test_should_not_create_without_acronym(self):
        new_campus = Campus()
        new_campus.name = "Facul Gama"
        new_campus.phone = "(61) 3333-3333"
        new_campus.address = "Setor Leste"
        new_campus.website_address = "https://fga.unb.br/"

        with self.assertRaises(ValidationError):
            new_campus.save()

    def test_should_not_create_without_phone(self):
        new_campus = Campus()
        new_campus.name = "Facul Gama"
        new_campus.acronym = "FGa"
        new_campus.address = "Setor Leste"
        new_campus.website_address = "https://fga.unb.br/"

        with self.assertRaises(ValidationError):
            new_campus.save()

    def test_should_not_create_without_address(self):
        new_campus = Campus()
        new_campus.name = "Facul Gama"
        new_campus.acronym = "FGa"
        new_campus.phone = "(61) 3333-3333"
        new_campus.website_address = "https://fga.unb.br/"

        with self.assertRaises(ValidationError):
            new_campus.save()

    def test_should_not_create_without_website_address(self):
        new_campus = Campus()
        new_campus.name = "Facul Gama"
        new_campus.acronym = "FGa"
        new_campus.phone = "(61) 3333-3333"
        new_campus.address = "Setor Leste"

        with self.assertRaises(ValidationError):
            new_campus.save()

    def test_read_a_existent_campus_by_acronym(self):
        campus = Campus.objects.get(acronym="FGA")

        self.assertEquals(campus, self.campus)

    def test_read_a_existent_campus_by_name(self):
        campus = Campus.objects.get(name="Campus da Faculdade Gama")

        self.assertEquals(campus, self.campus)

    def test_read_a_existent_campus_by_address(self):
        campus = Campus.objects.get(address="Setor Leste - Gama")

        self.assertEquals(campus, self.campus)

    def test_update_a_specific_campus(self):
        campus = Campus.objects.get(acronym="FGA")

        original_name = campus.name
        original_acronym = campus.acronym
        original_phone = campus.phone
        original_address = campus.address
        original_website_address = campus.website_address

        campus.name = "Faculdade Ceilândia"
        campus.acronym = "FCE"
        campus.phone = "(61) 4002-8922"
        campus.address = "P-sul"
        campus.website_address = "https://fce.unb.br/"
        campus.save()

        new_name = campus.name
        new_acronym = campus.acronym
        new_phone = campus.phone
        new_address = campus.address
        new_website_address = campus.website_address

        self.assertNotEquals(original_name, new_name)
        self.assertNotEquals(original_acronym, new_acronym)
        self.assertNotEquals(original_phone, new_phone)
        self.assertNotEquals(original_address, new_address)
        self.assertNotEquals(original_website_address, new_website_address)

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
