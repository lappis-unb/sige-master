from rest_framework import routers

from apps.measurements.views import (
    CumulativeMeasurementViewSet,
    InstantGraphViewSet,
    InstantMeasurementViewSet,
)

app_name = "minutely_measurements"

router = routers.DefaultRouter()

router.register(r"instant-measurements", InstantMeasurementViewSet, basename="instant-measurements")
router.register(r"cumulative-measurements", CumulativeMeasurementViewSet, basename="cumulative-measurements")
router.register(r"graph-instant-measurements", InstantGraphViewSet, basename="graph-instant")
