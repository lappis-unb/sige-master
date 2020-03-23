from rest_framework import routers

from .views import EnergyTransductorViewSet, EnergyTransductorListViewSet

app_name = "transductors"

router = routers.DefaultRouter()
router.register(r'energy-transductors', EnergyTransductorViewSet)
router.register(r'energy-transductors-list', 
                EnergyTransductorListViewSet,
                basename='energy-transductor-list')

urlpatterns = []
