from .views import *

from rest_framework import routers

app_name = "minutely_measurements"

router = routers.DefaultRouter()

router.register(r'minutely_measurements', MinutelyMeasurementViewSet)
router.register(r'quarterly_measurements', QuarterlyMeasurementViewSet)
router.register(r'monthly_measurements', MonthlyMeasurementViewSet)
router.register(r'realtime_measurements', RealTimeMeasurementViewSet)

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
    r'minutely_active_power',
    MinutelyActivePowerThreePhaseViewSet,
    basename='minutelyactivepower'
)

graph_router.register(
    r'minutely_reactive_power',
    MinutelyReactivePowerThreePhaseViewSet,
    basename='minutelyreactivepower'
)

graph_router.register(
    r'minutely_apparent_power',
    MinutelyApparentPowerThreePhaseViewSet,
    basename='minutelyapparentpower'
)

graph_router.register(
    r'minutely_power_factor',
    MinutelyPowerFactorThreePhaseViewSet,
    basename='minutelypowerfactor'
)

graph_router.register(
    r'minutely_dht_voltage',
    MinutelyDHTVoltageThreePhaseViewSet,
    basename='minutelydhtvoltage'
)

graph_router.register(
    r'minutely_dht_current',
    MinutelyDHTCurrentThreePhaseViewSet,
    basename='minutelydhtcurrent'
)

graph_router.register(
    r'minutely_total_active_power',
    MinutelyTotalActivePowerViewSet,
    basename='minutelytotalactivepower'
)

graph_router.register(
    r'minutely_total_reactive_power',
    MinutelyTotalReactivePowerViewSet,
    basename='minutelytotalreactivepower'
)

graph_router.register(
    r'minutely_total_apparent_power',
    MinutelyTotalApparentPowerViewSet,
    basename='minutelytotalapparentpower'
)

graph_router.register(
    r'minutely_total_power_factor',
    MinutelyTotalPowerFactorViewSet,
    basename='minutelytotalpowerfactor'
)

graph_router.register(
    r'quarterly_consumption_peak',
    ConsumptionPeakViewSet,
    basename='quarterlyconsumptionpeak'
)

graph_router.register(
    r'quarterly_consumption_off_peak',
    ConsumptionOffPeakViewSet,
    basename='quarterlyconsumptionoffpeak'
)

graph_router.register(
    r'quarterly_generated_energy_peak',
    GenerationPeakViewSet,
    basename='quarterlygenerationpeak'
)

graph_router.register(
    r'quarterly_generated_energy_off_peak',
    GenerationOffPeakViewSet,
    basename='quarterlygenerationoffpeak'
)
