from .views import *

from rest_framework import routers

router = routers.DefaultRouter()

router.register(
    r'voltage_related_events',
    VoltageRelatedEventViewSet,
    basename='voltage_related_events'
)
router.register(
    r'failed_connection_slave_events',
    FailedConnectionSlaveEventViewSet,
    basename='failed_connection_slave_events'
)
router.register(
    r'failed_connection_transductor_events',
    FailedConnectionTransductorEventViewSet,
    basename='failed_connection_transductor_events'
)
