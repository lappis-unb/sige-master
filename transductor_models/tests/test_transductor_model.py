import pytest
from django.test import TestCase
from transductor_models.models import TransductorModel
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError


class TransductorModelTestCase(TestCase):
    def setUp(self):
        self.sample_transductor_model = TransductorModel.objects.create(
            name='TR4020',
            transport_protocol='UDP',
            serial_protocol='ModbusRTU'
        )

    def test_create_transductor_model(self):
        size = len(TransductorModel.objects.all())

        transductor_model = TransductorModel.objects.create(
            name='TR2040',
            transport_protocol='TCP',
            serial_protocol='ModbusRTU'
        )

        self.assertIs(
            TransductorModel,
            transductor_model.__class__
        )
        self.assertEqual(size + 1, len(TransductorModel.objects.all()))

    def test_not_create_transductor_model_with_existent_name(self):
        size = len(TransductorModel.objects.all())

        with self.assertRaises(ValidationError):
            value = TransductorModel.objects.create(
                name='TR4020',
                transport_protocol='TCP',
                serial_protocol='ModbusRTU'
            )

        self.assertEqual(size, len(TransductorModel.objects.all()))

    def test_not_create_transductor_model_with_no_name(self):
        size = len(TransductorModel.objects.all())

        with self.assertRaises(ValidationError):
            value = TransductorModel.objects.create(
                transport_protocol='TCP',
                serial_protocol='ModbusRTU'
            )

        self.assertEqual(size, len(TransductorModel.objects.all()))

    def test_not_create_transductor_model_with_no_transport_protocol(self):
        size = len(TransductorModel.objects.all())

        with self.assertRaises(ValidationError):
            value = TransductorModel.objects.create(
                name='TR4020',
                serial_protocol='ModbusRTU'
            )

        self.assertEqual(size, len(TransductorModel.objects.all()))

    def test_not_create_transductor_model_with_no_serial_protocol(self):
        size = len(TransductorModel.objects.all())

        with self.assertRaises(ValidationError):
            value = TransductorModel.objects.create(
                name='TR4020',
                transport_protocol='TCP',
            )

        self.assertEqual(size, len(TransductorModel.objects.all()))

    def test_update_transductor_model_single_field(self):
        transductor_model = TransductorModel.objects.filter(name='TR4020')
        self.assertTrue(
            transductor_model.update(
                name='TR5050'
            )
        )

    def test_update_all_transductor_model_fields(self):
        transductor_model = TransductorModel.objects.filter(name='TR4020')
        self.assertTrue(
            transductor_model.update(
                name='TR5050',
                serial_protocol='UDP',
                transport_protocol='RTU'
            )
        )

    def test_not_update_transductor_model_with_existent_name(self):
        TransductorModel.objects.create(
            name='TR3030',
            transport_protocol='UDP',
            serial_protocol='ModbusRTU'
        )

        transductor_model = TransductorModel.objects.filter(name='TR4020')

        with self.assertRaises(IntegrityError):
            self.assertTrue(
                transductor_model.update(
                    name='TR3030',
                    serial_protocol='UDP',
                    transport_protocol='RTU'
                )
            )

    def test_retrieve_one_transductor_models(self):
        transductor_model = TransductorModel.objects.get(name='TR4020')

        self.assertIs(TransductorModel, transductor_model.__class__)

    def test_delete_transductor_model(self):
        transductor_model = TransductorModel.objects.get(name='TR4020')

        self.assertTrue(
            transductor_model.delete()
        )
