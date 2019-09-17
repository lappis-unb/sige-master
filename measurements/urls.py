from .views import *

from rest_framework import routers


app_name = "minutely_measurements"

router = routers.DefaultRouter()

router.register(r'minutely_measurements', MinutelyMeasurementViewSet)
router.register(r'quarterly_measurements', QuarterlyMeasurementViewSet)
router.register(r'monthly_measurements', MonthlyMeasurementViewSet)

graph_router = routers.DefaultRouter()

graph_router.register(
    r'minutely_threephase_voltage',
    VoltageThreePhaseViewSet,
    basename='minutelyvoltage'
)
graph_router.register(
    r'minutely_threephase_current',
    CurrentThreePhaseViewSet,
    basename='minutelycurrent'
)
