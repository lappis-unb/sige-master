# urls.py
from rest_framework_nested import routers
from .views import CampusViewSet
from django.urls import path
from django.urls import include

from .views import TariffViewSet
#from .views import CampusViewSet
#from rest_framework import routers


app_name = "campi"

router = routers.DefaultRouter()
router.register(r'campi', CampusViewSet)

# tariff_router = routers.NestedDefaultRouter(router, r'tariffs', lookup='tariff')
campi_router = routers.NestedSimpleRouter(router, r'campi', lookup='campi')
campi_router.register(r'tariffs', TariffViewSet, basename='campi-tariffs')

urlpatterns = [
    path('', include(router.urls)),
]
