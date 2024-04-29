from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from apps.memory_maps.views import MemoryMapViewSet

app_name = "memory_map"

router = DefaultRouter() if settings.DEBUG else SimpleRouter()
router.register(r"memory-map", MemoryMapViewSet, basename="memorymap")

urlpatterns = router.urls
