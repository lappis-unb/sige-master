from rest_framework import routers

from apps.measurements.views import (
    CumulativeGraphViewSet,
    CumulativeMeasurementViewSet,
    DailyProfileViewSet,
    InstantGraphViewSet,
    InstantMeasurementViewSet,
    ReportViewSet,
    UferViewSet,
)

app_name = "minutely_measurements"

router = routers.DefaultRouter()

router.register(r"measurements/instant", InstantMeasurementViewSet, basename="instant-measurements")
router.register(r"measurements/cumulative", CumulativeMeasurementViewSet, basename="cumulative-measurements")
router.register(r"graph/instant", InstantGraphViewSet, basename="graph-instant")
router.register(r"graph/cumulative", CumulativeGraphViewSet, basename="graph-cumulative")
router.register(r"graph/daily-profile", DailyProfileViewSet, basename="daily-profile")
router.register(r"reports/ufer", UferViewSet, basename="report-ufer")
router.register(r"reports/energy", ReportViewSet, basename="report-energy")
