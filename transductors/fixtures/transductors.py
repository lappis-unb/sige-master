import pytest
from transductors.models import EnergyTransductor
from transductors.fixtures.campi import campus_darcy
from transductors.fixtures.campi import campus_fga


@pytest.fixture
def transductor_darcy_1(campus_darcy):
    return EnergyTransductor.objects.create(
        serial_number="00000001",
        ip_address="10.0.0.1",
        firmware_version="0.1",
        model="EnergyTransductorModel",
        campus=campus_darcy
    )


@pytest.fixture
def transductor_darcy_2(campus_darcy):
    return EnergyTransductor.objects.create(
        serial_number="00000002",
        ip_address="10.0.0.2",
        firmware_version="0.1",
        model="EnergyTransductorModel",
        campus=campus_darcy
    )


@pytest.fixture
def transductor_fga_1(campus_fga):
    return EnergyTransductor.objects.create(
        serial_number="00000011",
        ip_address="10.0.1.1",
        firmware_version="0.1",
        model="EnergyTransductorModel",
        campus=campus_fga
    )


@pytest.fixture
def transductor_fga_2(campus_fga):
    return EnergyTransductor.objects.create(
        serial_number="00000012",
        ip_address="10.0.1.2",
        firmware_version="0.1",
        model="EnergyTransductorModel",
        campus=campus_fga
    )
