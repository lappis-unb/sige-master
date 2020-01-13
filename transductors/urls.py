from rest_framework import routers

from .views import EnergyTransductorViewSet

app_name = "transductors"

router = routers.DefaultRouter()
router.register(r'energy-transductors', EnergyTransductorViewSet)

urlpatterns = []
