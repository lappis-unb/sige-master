import pytest
import json
from django.test import TestCase
from users.models import CustomUser
from rest_framework.test import APIClient
from rest_framework import status
from transductors.fixtures.campi import campus_fga
from transductors.fixtures.campi import campus_darcy
from transductors.fixtures.transductors import transductor_darcy_1
from transductors.fixtures.transductors import transductor_darcy_2
from transductors.fixtures.transductors import transductor_fga_1
from transductors.fixtures.transductors import transductor_fga_2

from transductors.models import EnergyTransductor
from campi.models import Campus


@pytest.fixture
def transductors_darcy(transductor_darcy_1, transductor_darcy_2):
    return [transductor_darcy_1, transductor_darcy_2]


@pytest.fixture
def transductors_fga(transductor_fga_1, transductor_fga_2):
    return [transductor_fga_1, transductor_fga_2]


@pytest.fixture
def all_transductors(transductors_darcy, transductors_fga):
    return [*transductors_darcy, *transductors_fga]


@pytest.mark.django_db
class TestTransductorsEndpoints:
    def setup_method(self):
        self._api_client = APIClient()
        self._base_endpoint = ("/energy-transductors/")

    def test_get_all_transductors(self, all_transductors):
        endpoint = self._base_endpoint

        response = json.loads(self._api_client.get(endpoint).content)

        assert len(all_transductors) == len(response)

    def test_get_transdutors_from_fga_in_list_with_only_fga_transductors(
            self, campus_fga, transductors_fga):
        params = f"?campus_id={campus_fga.id}"
        endpoint = self._base_endpoint + params

        response = json.loads(self._api_client.get(endpoint).content)

        self._api_client.logout()
        assert len(transductors_fga) == len(response)

    def test_filter_transdutors_from_darcy_in_list_with_all_transductors(
            self, campus_darcy, all_transductors, transductors_darcy):
        params = f"?campus_id={campus_darcy.id}"
        endpoint = self._base_endpoint + params

        transductors_response = json.loads(
            self._api_client.get(endpoint).content
        )

        self._api_client.logout()

        real_transductor_serial_numbers = [
            transductor.serial_number for transductor in transductors_darcy]
        obtained_transductor_serial_numbers = [
            transductor['serial_number']
            for transductor in transductors_response]

        assert len(transductors_darcy) == len(transductors_response)
        assert all(
            real_serial_number in obtained_transductor_serial_numbers
            for real_serial_number in real_transductor_serial_numbers)
