from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from apps.events.views import (
    CumulativeMeasurementTriggerViewSet,
    EventTypeViewSet,
    EventViewSet,
    InstantMeasurementTriggerViewSet,
)

app_name = "events"

router = DefaultRouter() if settings.DEBUG else SimpleRouter()
router.register(r"events", EventViewSet, basename="events")
router.register(r"event-types", EventTypeViewSet, basename="event-types")
router.register(r"instant-triggers", InstantMeasurementTriggerViewSet, basename="instant-triggers")
router.register(r"cumulative-triggers", CumulativeMeasurementTriggerViewSet, basename="cumulative-triggers")


urlpatterns = router.urls
