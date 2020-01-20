from .views import *

from rest_framework import routers

router = routers.DefaultRouter()

router.register(
    r'voltage-related-events',
    VoltageRelatedEventViewSet,
    basename='voltage-related-events'
)
router.register(
    r'failed-connection-slave-events',
    FailedConnectionSlaveEventViewSet,
    basename='failed-connection-slave-events'
)
router.register(
    r'failed-connection-transductor-events',
    FailedConnectionTransductorEventViewSet,
    basename='failed-connection-transductor-events'
)
router.register(
    r'occurences',
    AllEventsViewSet,
    basename='occurences'
)
