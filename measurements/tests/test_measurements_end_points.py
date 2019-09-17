from django.test import TestCase
from rest_framework.test import APIClient
from users.models import CustomUser
from rest_framework import status


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
        self.__reactive_power_minutely_end_point = "/chart/minutely"
        self.__reactive_power_minutely_end_point += "_reactive_power/"

    def test_get_with_auth_reactive_power_minutely_end_point(self):
        self.__api_client.login(username="admin", password="admin")
        response = self.__api_client.get(
            self.__reactive_power_minutely_end_point)
        self.__api_client.logout()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_without_auth_reactive_power_minutely_end_point(self):
        response = self.__api_client.get(
            self.__reactive_power_minutely_end_point)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_with_auth_reactive_power_minutely_end_point(self):
        self.__api_client.login(username="admin", password="admin")
        response = self.__api_client.post(
            self.__reactive_power_minutely_end_point)
        self.__api_client.logout()
        self.assertEqual(response.status_code,
                         status.HTTP_401_UNAUTHORIZED)

    def test_post_without_auth_reactive_power_minutely_end_point(self):
        response = self.__api_client.post(
            self.__reactive_power_minutely_end_point)
        self.assertEqual(response.status_code,
                         status.HTTP_401_UNAUTHORIZED)

    def test_put_with_auth_reactive_power_minutely_end_point(self):
        self.__api_client.login(username="admin", password="admin")
        response = self.__api_client.put(
            self.__reactive_power_minutely_end_point)
        self.__api_client.logout()
        self.assertEqual(response.status_code,
                         status.HTTP_401_UNAUTHORIZED)

    def test_put_without_auth_reactive_power_minutely_end_point(self):
        response = self.__api_client.put(
            self.__reactive_power_minutely_end_point)
        self.assertEqual(response.status_code,
                         status.HTTP_401_UNAUTHORIZED)

    def test_delete_with_auth_reactive_power_minutely_end_point(self):
        self.__api_client.login(username="admin", password="admin")
        response = self.__api_client.delete(
            self.__reactive_power_minutely_end_point)
        self.__api_client.logout()
        self.assertEqual(response.status_code,
                         status.HTTP_401_UNAUTHORIZED)

    def test_delete_without_auth_reactive_power_minutely_end_point(self):
        response = self.__api_client.delete(
            self.__reactive_power_minutely_end_point)
        self.assertEqual(response.status_code,
                         status.HTTP_401_UNAUTHORIZED)
