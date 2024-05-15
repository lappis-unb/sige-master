from rest_framework import routers

from apps.measurements.views import (
    CumulativeGraphViewSet,
    CumulativeMeasurementViewSet,
    InstantGraphViewSet,
    InstantMeasurementViewSet,
    ReportViewSet,
    UferViewSet,
)

app_name = "minutely_measurements"

router = routers.DefaultRouter()

router.register(r"instant-measurements", InstantMeasurementViewSet, basename="instant-measurements")
router.register(r"cumulative-measurements", CumulativeMeasurementViewSet, basename="cumulative-measurements")
router.register(r"graph-instant-measurements", InstantGraphViewSet, basename="graph-instant")
router.register(r"graph-cumulative-measurements", CumulativeGraphViewSet, basename="graph-cumulative")
router.register(r"report-ufer", UferViewSet, basename="report-ufer")
router.register(r"report-energy", ReportViewSet, basename="report-energy")
