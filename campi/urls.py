from rest_framework_nested import routers

from django.urls import path
from django.urls import include

from .views import TariffViewSet
from .views import CampusViewSet


app_name = "campi"

router = routers.DefaultRouter()
router.register(r'campi', CampusViewSet)

campi_router = routers.NestedDefaultRouter(router, r'campi', lookup='campi')
campi_router.register(r'tariffs', TariffViewSet, basename='tariffs')


urlpatterns = [
    path('', include(campi_router.urls)),
]
