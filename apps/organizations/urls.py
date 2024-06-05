from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from apps.organizations.views import EntityViewSet, OrganizationViewSet

app_name = "organizations"

router = DefaultRouter() if settings.DEBUG else SimpleRouter()
router.register(r"entities", EntityViewSet)
router.register(r"organizations", OrganizationViewSet)

urlpatterns = router.urls
