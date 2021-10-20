from django.utils import timezone
import json
from django.test import TestCase
from users.models import CustomUser

from rest_framework.test import APIClient
from rest_framework import status

from measurements.models import EnergyTransductor
from measurements.models import MinutelyMeasurement
from campi.models import Campus


class MeasurementsEndPointsTestCase(TestCase):
    def setUp(self):
        self.__user = CustomUser.objects.create(email="admin@admin.com",
                                                password="admin")
        self.__user.save()
        self.__credentials = ("admin@admin.com", "admin")
        self.__api_client = APIClient()
        self.__minutely_three_phase = (
            "/graph/minutely-threephase-voltage/"
        )
        self.__minutely_simple_phase = (
            "/graph/minutely-total-active-power/"
        )

        self.campus = Campus.objects.create(
            name='UnB - Faculdade Gama',
            acronym='FGA',
        )

        self.transductor = EnergyTransductor.objects.create(
            serial_number="12345678",
            ip_address="1.1.1.1",
            firmware_version="0.1",
            model="EnergyTransductorModel",
            campus=self.campus
        )

    def test_get_with_auth_minutely_three_phase(self):
        self.measurement_1 = MinutelyMeasurement.objects.create(
            transductor_id=self.transductor.id,
            collection_date=timezone.datetime(2021, 1, 13, 0, 0, 0),
            voltage_a=220.2,
            voltage_b=220.3,
            voltage_c=220.4
        )

        self.measurement_2 = MinutelyMeasurement.objects.create(
            transductor_id=self.transductor.id,
            collection_date=timezone.datetime(2021, 1, 13, 0, 10, 0),
            voltage_a=225.1,
            voltage_b=218.2,
            voltage_c=217.3
        )

        params = "?id={}&start_date={}".format(
            self.transductor.id,
            "2021-01-01 00:00:00",
        )
        endpoint = self.__minutely_three_phase + params

        self.__api_client.login(email="admin@admin.com", password="admin")

        response = self.__api_client.get(endpoint)
        content = json.loads(response.content)[0]

        self.__api_client.logout()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(2, len(content['phase_a']))
        self.assertEqual(2, len(content['phase_b']))
        self.assertEqual(2, len(content['phase_c']))
        self.assertEqual(225.1, content['max'])
        self.assertEqual(217.3, content['min'])
        self.assertEqual(
            ['01/13/2021 00:00:00', 220.2],
            content['phase_a'][0]
        )
        self.assertEqual(
            ['01/13/2021 00:10:00', 225.1],
            content['phase_a'][1]
        )

    def test_get_with_auth_minutely_three_phase(self):
        self.measurement_1 = MinutelyMeasurement.objects.create(
            transductor_id=self.transductor.id,
            collection_date=timezone.datetime(2021, 1, 13, 0, 0, 0),
            voltage_a=220.2,
            voltage_b=220.3,
            voltage_c=220.4
        )

        self.measurement_2 = MinutelyMeasurement.objects.create(
            transductor_id=self.transductor.id,
            collection_date=timezone.datetime(2021, 1, 13, 0, 11, 0),
            voltage_a=225.1,
            voltage_b=218.2,
            voltage_c=217.3
        )

        params = "?id={}&start_date={}".format(
            self.transductor.id,
            "2021-01-01 00:00:00",
        )
        endpoint = self.__minutely_three_phase + params

        self.__api_client.login(email="admin@admin.com", password="admin")

        response = self.__api_client.get(endpoint)
        content = json.loads(response.content)[0]

        phase_a_measurements = content['phase_a']

        self.__api_client.logout()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(12, len(content['phase_a']))
        self.assertEqual(12, len(content['phase_b']))
        self.assertEqual(12, len(content['phase_c']))
        self.assertEqual(225.1, content['max'])
        self.assertEqual(217.3, content['min'])
        self.assertEqual(
            ['01/13/2021 00:00:00', 220.2],
            phase_a_measurements[0]
        )
        self.assertEqual(
            ['01/13/2021 00:01:00', 0],
            phase_a_measurements[1]
        )
        self.assertEqual(
            ['01/13/2021 00:10:00', 0],
            phase_a_measurements[10]
        )
        self.assertEqual(
            ['01/13/2021 00:11:00', 225.1],
            phase_a_measurements[11]
        )

    def test_get_with_auth_minutely_three_phase_lttb_filter(self):
        self.measurement_1 = MinutelyMeasurement.objects.create(
            transductor_id=self.transductor.id,
            collection_date=timezone.datetime(2021, 1, 13, 0, 0, 0),
            voltage_a=220.2,
            voltage_b=220.3,
            voltage_c=220.4
        )

        self.measurement_2 = MinutelyMeasurement.objects.create(
            transductor_id=self.transductor.id,
            collection_date=timezone.datetime(2021, 1, 13, 0, 11, 0),
            voltage_a=225.1,
            voltage_b=218.2,
            voltage_c=217.3
        )

        params = "?id={}&start_date={}&is_filtered={}".format(
            self.transductor.id,
            "2021-01-01 00:00:00",
            "True"
        )
        endpoint = self.__minutely_three_phase + params

        self.__api_client.login(email="admin@admin.com", password="admin")

        response = self.__api_client.get(endpoint)
        content = json.loads(response.content)[0]

        phase_a_measurements = content['phase_a']

        self.__api_client.logout()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(12, len(content['phase_a']))
        self.assertEqual(12, len(content['phase_b']))
        self.assertEqual(12, len(content['phase_c']))
        self.assertEqual(
            ['01/13/2021 00:00:00', 220.2],
            phase_a_measurements[0]
        )
        self.assertEqual(
            ['01/13/2021 00:01:00', 0],
            phase_a_measurements[1]
        )
        self.assertEqual(
            ['01/13/2021 00:10:00', 0],
            phase_a_measurements[10]
        )
        self.assertEqual(
            ['01/13/2021 00:11:00', 225.1],
            phase_a_measurements[11]
        )

    def test_get_without_auth_minutely_three_phase(self):
        params = "?id={}&start_date={}&end_date={}".format(
            self.transductor.id,
            "2019-01-01 00:00:00",
            "2019-01-01 23:59:00"
        )

        endpoint = self.__minutely_three_phase + params
        response = self.__api_client.get(endpoint)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_with_auth_minutely_simple_phase(self):
        self.measurement_1 = MinutelyMeasurement.objects.create(
            transductor_id=self.transductor.id,
            collection_date=timezone.datetime(2021, 1, 13, 0, 0, 0),
            total_active_power=2200
        )

        self.measurement_2 = MinutelyMeasurement.objects.create(
            transductor_id=self.transductor.id,
            collection_date=timezone.datetime(2021, 1, 13, 0, 10, 0),
            total_active_power=2250
        )

        params = "?id={}&start_date={}".format(
            self.transductor.id,
            "2021-01-01 00:00:00"
        )
        endpoint = self.__minutely_simple_phase + params

        self.__api_client.login(email="admin@admin.com", password="admin")

        response = self.__api_client.get(endpoint)
        content = json.loads(response.content)[0]

        measurements = content['measurements']

        self.__api_client.logout()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(2, len(measurements))
        self.assertEqual(2250, content['max'])
        self.assertEqual(2200, content['min'])
        self.assertEqual(
            ['01/13/2021 00:00:00', 2200],
            measurements[0]
        )
        self.assertEqual(
            ['01/13/2021 00:10:00', 2250],
            measurements[1]
        )

    def test_post_with_auth_minutely_three_phase(self):
        self.__api_client.login(email="admin@admin.com", password="admin")

        response = self.__api_client.post(
            self.__minutely_three_phase)

        self.__api_client.logout()
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_post_without_auth_minutely_three_phase(self):
        response = self.__api_client.post(
            self.__minutely_three_phase)

        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put_with_auth_minutely_three_phase(self):
        self.__api_client.login(email="admin@admin.com", password="admin")

        response = self.__api_client.put(
            self.__minutely_three_phase)

        self.__api_client.logout()
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put_without_auth_minutely_three_phase(self):
        response = self.__api_client.put(
            self.__minutely_three_phase)

        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_with_auth_minutely_three_phase(self):
        self.__api_client.login(email="admin@admin.com", password="admin")

        response = self.__api_client.delete(
            self.__minutely_three_phase)

        self.__api_client.logout()
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_without_auth_minutely_three_phase(self):
        response = self.__api_client.delete(
            self.__minutely_three_phase)

        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)
