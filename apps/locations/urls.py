from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from apps.locations.views import AddressViewSet, GeographicLocationViewSet

app_name = "locations"

router = DefaultRouter() if settings.DEBUG else SimpleRouter()
router.register(r'addresses', AddressViewSet)
router.register(r'geographic-locations', GeographicLocationViewSet)

urlpatterns = router.urls
