import pytest
from django.test import TestCase
from transductor_models.models import TransductorModel
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError


class TransductorModelTestCase(TestCase):
    def setUp(self):
        self.transductor_model = TransductorModel()
        self.transductor_model.model_code = "987654321"
        self.transductor_model.name = "TR4020"
        self.transductor_model.serial_protocol = "UDP"
        self.transductor_model.transport_protocol = "modbus"
        self.transductor_model.minutely_register_addresses = [[1, 1]]
        self.transductor_model.quarterly_register_addresses = [[1, 1]]
        self.transductor_model.monthly_register_addresses = [[1, 1]]
        self.transductor_model.save(bypass_requests=True)

    def test_create_transductor_model(self):
        size = len(TransductorModel.objects.all())

        transductor_model = TransductorModel()
        transductor_model.model_code = "123456789"
        transductor_model.name = "TR2040"
        transductor_model.serial_protocol = "UDP"
        transductor_model.transport_protocol = "modbus"
        transductor_model.minutely_register_addresses = [[1, 1]]
        transductor_model.quarterly_register_addresses = [[1, 1]]
        transductor_model.monthly_register_addresses = [[1, 1]]
        transductor_model.save(bypass_requests=True)

        self.assertIs(
            TransductorModel,
            transductor_model.__class__
        )
        self.assertEqual(size + 1, len(TransductorModel.objects.all()))

    def test_not_create_transductor_model_with_existent_name(self):
        size = len(TransductorModel.objects.all())

        transductor_model = TransductorModel()
        transductor_model.model_code = "123456789"
        transductor_model.name = "TR4020"
        transductor_model.serial_protocol = "UDP"
        transductor_model.transport_protocol = "modbus"
        transductor_model.minutely_register_addresses = [[1, 1]]
        transductor_model.quarterly_register_addresses = [[1, 1]]
        transductor_model.monthly_register_addresses = [[1, 1]]

        with self.assertRaises(ValidationError):
            transductor_model.save(bypass_requests=True)

        self.assertEqual(size, len(TransductorModel.objects.all()))

    def test_not_create_transductor_model_with_no_name(self):
        size = len(TransductorModel.objects.all())

        transductor_model = TransductorModel()
        transductor_model.model_code = "123456789"
        transductor_model.name = "TR4020"
        transductor_model.serial_protocol = "UDP"
        transductor_model.transport_protocol = "modbus"
        transductor_model.minutely_register_addresses = [[1, 1]]
        transductor_model.quarterly_register_addresses = [[1, 1]]
        transductor_model.monthly_register_addresses = [[1, 1]]

        with self.assertRaises(ValidationError):
            transductor_model.save(bypass_requests=True)

        self.assertEqual(size, len(TransductorModel.objects.all()))

    def test_not_create_transductor_model_with_no_transport_protocol(self):
        size = len(TransductorModel.objects.all())

        transductor_model = TransductorModel()
        transductor_model.model_code = "123456789"
        transductor_model.name = "TR4020"
        transductor_model.transport_protocol = "modbus"
        transductor_model.minutely_register_addresses = [[1, 1]]
        transductor_model.quarterly_register_addresses = [[1, 1]]
        transductor_model.monthly_register_addresses = [[1, 1]]

        with self.assertRaises(ValidationError):
            transductor_model.save(bypass_requests=True)

        self.assertEqual(size, len(TransductorModel.objects.all()))

    def test_not_create_transductor_model_with_no_serial_protocol(self):
        size = len(TransductorModel.objects.all())

        transductor_model = TransductorModel()
        transductor_model.model_code = "123456789"
        transductor_model.name = "TR2020"
        transductor_model.transport_protocol = "modbus"
        transductor_model.minutely_register_addresses = [[1, 1]]
        transductor_model.quarterly_register_addresses = [[1, 1]]
        transductor_model.monthly_register_addresses = [[1, 1]]

        with self.assertRaises(ValidationError):
            transductor_model.save(bypass_requests=True)

        self.assertEqual(size, len(TransductorModel.objects.all()))

    def test_update_transductor_model_single_field(self):
        transductor_model = TransductorModel.objects.filter(
            model_code="987654321"
        )
        self.assertTrue(
            transductor_model.update(
                name='TR5050'
            )
        )

    def test_update_all_transductor_model_fields(self):
        transductor_model = TransductorModel.objects.filter(
            model_code="987654321"
        )
        self.assertTrue(
            transductor_model.update(
                name='TR5050',
                serial_protocol='UDP',
                transport_protocol='RTU',
                minutely_register_addresses=[[1, 2]],
                quarterly_register_addresses=[[1, 2]],
                monthly_register_addresses=[[1, 2]]
            )
        )

    def test_retrieve_one_transductor_models(self):
        transductor_model = TransductorModel.objects.get(model_code="987654321")

        self.assertIs(TransductorModel, transductor_model.__class__)

    def test_delete_transductor_model(self):
        transductor_model = TransductorModel.objects.get(model_code="987654321")

        self.assertIsNone(
            transductor_model.delete()
        )
