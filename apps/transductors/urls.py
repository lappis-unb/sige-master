from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from apps.transductors.views import (
    TransductorModelViewSet,
    TransductorStatusViewSet,
    TransductorViewSet,
)

app_name = "transductors"

router = DefaultRouter() if settings.DEBUG else SimpleRouter()
router.register(r'energy-transductors', TransductorViewSet, basename='transductor')
router.register(r'transductors-model', TransductorModelViewSet, basename="model")
router.register(r'transductors-status', TransductorStatusViewSet, basename="status")

urlpatterns = router.urls
