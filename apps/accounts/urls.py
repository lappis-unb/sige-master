from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from apps.accounts.views import AccountViewSet

app_name = "accounts"

router = DefaultRouter() if settings.DEBUG else SimpleRouter()
router.register("accounts", AccountViewSet, basename="accounts")


urlpatterns = router.urls
