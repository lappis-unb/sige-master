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
graph_router.register(
    r'minutely_frequency',
    FrequencyViewSet,
    basename='minutelyfrequency'
)

graph_router.register(
    r'minutely_voltage',
    measurements_views.MinutelyVoltageThreePhaseViewSet,
    basename='minutelyvoltage'
)

graph_router.register(
    r'minutely_current',
    measurements_views.MinutelyCurrentThreePhaseViewSet,
    basename='minutelycurrent'
)

graph_router.register(
    r'minutely_active_power',
    measurements_views.MinutelyActivePowerThreePhaseViewSet,
    basename='minutelyactivepower'
)

graph_router.register(
    r'minutely_reactive_power',
    measurements_views.MinutelyReactivePowerThreePhaseViewSet,
    basename='minutelyreactivepower'
)

graph_router.register(
    r'minutely_apparent_power',
    measurements_views.MinutelyApparentPowerThreePhaseViewSet,
    basename='minutelyapparentpower'
)

graph_router.register(
    r'minutely_power_factor',
    measurements_views.MinutelyPowerFactorThreePhaseViewSet,
    basename='minutelypowerfactor'
)

graph_router.register(
    r'minutely_dht_voltage',
    measurements_views.MinutelyDHTVoltageThreePhaseViewSet,
    basename='minutelydhtvoltage'
)

graph_router.register(
    r'minutely_dht_current',
    measurements_views.MinutelyDHTCurrentThreePhaseViewSet,
    basename='minutelydhtcurrent'
)

graph_router.register(
    r'minutely_frequency',
    measurements_views.MinutelyFrequencyViewSet,
    basename='minutelyfrequency'
)

graph_router.register(
    r'minutely_total_active_power',
    measurements_views.MinutelyTotalActivePowerViewSet,
    basename='minutelytotalactivepower'
)

graph_router.register(
    r'minutely_total_reactive_power',
    measurements_views.MinutelyTotalReactivePowerViewSet,
    basename='minutelytotalreactivepower'
)

graph_router.register(
    r'minutely_total_apparent_power',
    measurements_views.MinutelyTotalApparentPowerViewSet,
    basename='minutelytotalapparentpower'
)

graph_router.register(
    r'minutely_total_power_factor',
    measurements_views.MinutelyTotalPowerFactorViewSet,
    basename='minutelytotalpowerfactor'
)
