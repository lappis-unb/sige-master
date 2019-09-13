# import pytest
# from django.test import TestCase
# from django.conf import settings
# from django.db import IntegrityError

# from measurements.models import MinutelyMeasurement
# from measurements.models import QuarterlyMeasurement
# from measurements.models import MonthlyMeasurement
# from slaves.models import Slave
# from transductors.models import EnergyTransductor
# from transductor_models.models import TransductorModel
# from datetime import datetime


# class MeasurementsTestCase(TestCase):

#     def setUp(self):
#         self.slave = Slave.objects.create(
#             ip_address="1.1.1.1",
#             location="UED FGA",
#             broken=False
#         )

#         self.transductor_model = TransductorModel.objects.create(
#             name="TR4020",
#             serial_protocol="UDP",
#             transport_protocol="modbus"
#         )

#         self.transductor = EnergyTransductor.objects.create(
#             serial_number="12345678",
#             ip_address="1.1.1.1",
#             model=self.transductor_model
#         )

#         self.transductor.slave_servers.add(self.slave)

#         self.time = datetime.now()

#         self.minutely_measurements = MinutelyMeasurement.objects.create(
#             transductor=self.transductor,
#             collection_time=self.time
#         )

#         self.quarterly_measurements = QuarterlyMeasurement.objects.create(
#             transductor=self.transductor,
#             collection_time=self.time
#         )

#         self.monthly_measurements = MonthlyMeasurement.objects.create(
#             transductor=self.transductor,
#             collection_time=self.time
#         )

#     # Minutely measurements tests

#     def test_create_new_minutely_measurement(self):
#         before = len(MinutelyMeasurement.objects.all())
#         MinutelyMeasurement.objects.create(
#             transductor=self.transductor,
#             collection_time=datetime.now()
#         )
#         after = len(MinutelyMeasurement.objects.all())

#         self.assertEqual(before + 1, after)

#     def test_should_not_create_minutely_measurement_without_collection_time(
#             self):
#         new_measurement = MinutelyMeasurement()
#         new_measurement.transductor = self.transductor

#         with self.assertRaises(IntegrityError):
#             new_measurement.save()

#     def test_should_not_create_minutely_measurement_without_transductor(self):
#         new_measurement = MinutelyMeasurement()
#         new_measurement.collection_time = datetime.now()

#         with self.assertRaises(IntegrityError):
#             new_measurement.save()

#     def test_delete_a_existent_minutely_measurement(self):
#         measurements = MinutelyMeasurement.objects.last()
#         self.assertTrue(measurements.delete())

#     # Quarterly measurements tests
#     def test_create_new_quarterly_measurement(self):
#         before = len(QuarterlyMeasurement.objects.all())
#         QuarterlyMeasurement.objects.create(
#             transductor=self.transductor,
#             collection_time=datetime.now()
#         )
#         after = len(QuarterlyMeasurement.objects.all())

#         self.assertEqual(before + 1, after)

#     def test_should_not_create_quarterly_measurement_without_collection_time(
#             self):
#         new_measurement = QuarterlyMeasurement()
#         new_measurement.transductor = self.transductor

#         with self.assertRaises(IntegrityError):
#             new_measurement.save()

#     def test_should_not_create_quarterly_measurement_without_transductor(self):
#         new_measurement = QuarterlyMeasurement()
#         new_measurement.collection_time = datetime.now()

#         with self.assertRaises(IntegrityError):
#             new_measurement.save()

#     def test_delete_a_existent_quarterly_measurement(self):
#         measurements = QuarterlyMeasurement.objects.last()
#         self.assertTrue(measurements.delete())

#     # Monthly measurements tests
#     def test_create_new_monthly_measurement(self):
#         before = len(MonthlyMeasurement.objects.all())
#         MonthlyMeasurement.objects.create(
#             transductor=self.transductor,
#             collection_time=datetime.now()
#         )
#         after = len(MonthlyMeasurement.objects.all())

#         self.assertEqual(before + 1, after)

#     def test_should_not_create_monthly_measurement_without_collection_time(
#             self):
#         new_measurement = MonthlyMeasurement()
#         new_measurement.transductor = self.transductor

#         with self.assertRaises(IntegrityError):
#             new_measurement.save()

#     def test_should_not_create_monthly_measurement_without_transductor(self):
#         new_measurement = MonthlyMeasurement()
#         new_measurement.collection_time = datetime.now()

#         with self.assertRaises(IntegrityError):
#             new_measurement.save()

#     def test_delete_a_existent_monthly_measurement(self):
#         measurements = MonthlyMeasurement.objects.last()
#         self.assertTrue(measurements.delete())
