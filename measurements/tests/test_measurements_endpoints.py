from django.test import TestCase
from rest_framework.test import APIClient
from users.models import CustomUser
from rest_framework import status
from measurements.models import EnergyTransductor


class MeasurementsEndPointsTestCase(TestCase):
    def setUp(self):
        self.__user = CustomUser.objects.create(username="admin",
                                                email="admin@admin.com",
                                                name="Admin's name",
                                                user_type="adm",
                                                password="admin")
        self.__user.save()
        self.__credentials = ("admin", "admin")
        self.__api_client = APIClient()
        self.__minutely_three_phase = (
            "/graph/minutely_threephase_voltage/"
        )

        self.transductor = EnergyTransductor.objects.create(
            serial_number="12345678",
            ip_address="1.1.1.1",
            firmware_version="0.1",
            model="EnergyTransductorModel"
        )

    def test_get_with_auth_minutely_three_phase(self):
        params = "?serial_number={}&start_date={}&end_date={}".format(
            self.transductor.serial_number,
            "2019-01-01 00:00",
            "2019-01-01 23:59"
        )
        endpoint = self.__minutely_three_phase + params
        self.__api_client.login(username="admin", password="admin")
        response = self.__api_client.get(endpoint)
        self.__api_client.logout()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_without_auth_minutely_three_phase(self):
        params = "?serial_number={}&start_date={}&end_date={}".format(
            self.transductor.serial_number,
            "2019-01-01 00:00",
            "2019-01-01 23:59"
        )
        endpoint = self.__minutely_three_phase + params
        response = self.__api_client.get(endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_with_auth_minutely_three_phase(self):
        self.__api_client.login(username="admin", password="admin")
        response = self.__api_client.post(
            self.__minutely_three_phase)
        self.__api_client.logout()
        self.assertEqual(response.status_code,
                         status.HTTP_401_UNAUTHORIZED)

    def test_post_without_auth_minutely_three_phase(self):
        response = self.__api_client.post(
            self.__minutely_three_phase)
        self.assertEqual(response.status_code,
                         status.HTTP_401_UNAUTHORIZED)

    def test_put_with_auth_minutely_three_phase(self):
        self.__api_client.login(username="admin", password="admin")
        response = self.__api_client.put(
            self.__minutely_three_phase)
        self.__api_client.logout()
        self.assertEqual(response.status_code,
                         status.HTTP_401_UNAUTHORIZED)

    def test_put_without_auth_minutely_three_phase(self):
        response = self.__api_client.put(
            self.__minutely_three_phase)
        self.assertEqual(response.status_code,
                         status.HTTP_401_UNAUTHORIZED)

    def test_delete_with_auth_minutely_three_phase(self):
        self.__api_client.login(username="admin", password="admin")
        response = self.__api_client.delete(
            self.__minutely_three_phase)
        self.__api_client.logout()
        self.assertEqual(response.status_code,
                         status.HTTP_401_UNAUTHORIZED)

    def test_delete_without_auth_minutely_three_phase(self):
        response = self.__api_client.delete(
            self.__minutely_three_phase)
        self.assertEqual(response.status_code,
                         status.HTTP_401_UNAUTHORIZED)
