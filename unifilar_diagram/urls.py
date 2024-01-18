from .views import PowerSwitchViewSet, TransmissionLineViewSet, LocationViewSet, DrawViewSet

from rest_framework import routers

app_name = "lines"

router = routers.DefaultRouter()
router.register(r'location', LocationViewSet)
router.register(r'lines', TransmissionLineViewSet)
router.register(r'switch', PowerSwitchViewSet)
router.register(r'draw', DrawViewSet, basename='draw')