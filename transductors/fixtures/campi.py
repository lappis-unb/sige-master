import pytest
from campi.models import Campus


@pytest.fixture
def campus_darcy():
    return Campus.objects.create(
        name='Darcy Ribeiro - Gleba A',
        acronym='Darcy A'
    )


@pytest.fixture
def campus_fga():
    return Campus.objects.create(
        name='UnB - Faculdade Gama',
        acronym='FGA'
    )
