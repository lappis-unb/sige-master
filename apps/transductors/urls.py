from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from apps.transductors.views import (
    TransductorModelViewSet,
    TransductorStatusViewSet,
    TransductorViewSet,
)

app_name = "transductors"

router = DefaultRouter() if settings.DEBUG else SimpleRouter()
router.register(r"transductors", TransductorViewSet, basename="transductor")
router.register(r"transductor-models", TransductorModelViewSet, basename="model")
router.register(r"transductor-status", TransductorStatusViewSet, basename="status")

urlpatterns = router.urls
