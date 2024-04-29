from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from apps.events.views import EventTypeViewSet, EventViewSet, MeasurementTriggerViewSet

app_name = "events"

router = DefaultRouter() if settings.DEBUG else SimpleRouter()
router.register(r"events", EventViewSet, basename="events")
router.register(r"event-types", EventTypeViewSet, basename="event-types")
router.register(r"measurement-triggers", MeasurementTriggerViewSet, basename="measurement-triggers")


urlpatterns = router.urls
