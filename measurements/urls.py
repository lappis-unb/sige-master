from measurements import views

from rest_framework import routers

app_name = "minutely_measurements"

router = routers.DefaultRouter()

router.register(r'minutely_measurements', views.MinutelyMeasurementViewSet)
router.register(r'quarterly_measurements', views.QuarterlyMeasurementViewSet)
router.register(r'monthly_measurements', views.MonthlyMeasurementViewSet)

graph_router = routers.DefaultRouter()

graph_router.register(
    r'minutely_threephase_voltage',
    views.VoltageThreePhaseViewSet,
    basename='minutelyvoltage'
)
graph_router.register(
    r'minutely_threephase_current',
    views.CurrentThreePhaseViewSet,
    basename='minutelycurrent'
)
graph_router.register(
    r'minutely_frequency',
    views.FrequencyViewSet,
    basename='minutelyfrequency'
)

graph_router.register(
    r'minutely_active_power',
    views.MinutelyActivePowerThreePhaseViewSet,
    basename='minutelyactivepower'
)

graph_router.register(
    r'minutely_reactive_power',
    views.MinutelyReactivePowerThreePhaseViewSet,
    basename='minutelyreactivepower'
)

graph_router.register(
    r'minutely_apparent_power',
    views.MinutelyApparentPowerThreePhaseViewSet,
    basename='minutelyapparentpower'
)

graph_router.register(
    r'minutely_power_factor',
    views.MinutelyPowerFactorThreePhaseViewSet,
    basename='minutelypowerfactor'
)

graph_router.register(
    r'minutely_dht_voltage',
    views.MinutelyDHTVoltageThreePhaseViewSet,
    basename='minutelydhtvoltage'
)

graph_router.register(
    r'minutely_dht_current',
    views.MinutelyDHTCurrentThreePhaseViewSet,
    basename='minutelydhtcurrent'
)

graph_router.register(
    r'minutely_total_active_power',
    views.MinutelyTotalActivePowerViewSet,
    basename='minutelytotalactivepower'
)

graph_router.register(
    r'minutely_total_reactive_power',
    views.MinutelyTotalReactivePowerViewSet,
    basename='minutelytotalreactivepower'
)

graph_router.register(
    r'minutely_total_apparent_power',
    views.MinutelyTotalApparentPowerViewSet,
    basename='minutelytotalapparentpower'
)

graph_router.register(
    r'minutely_total_power_factor',
    views.MinutelyTotalPowerFactorViewSet,
    basename='minutelytotalpowerfactor'
)

graph_router.register(
    r'quarterly_consumption_peak',
    views.ConsumptionPeakViewSet,
    basename='quarterlyconsumptionpeak'
)

graph_router.register(
    r'quarterly_consumption_off_peak',
    views.ConsumptionOffPeakViewSet,
    basename='quarterlyconsumptionoffpeak'
)

graph_router.register(
    r'quarterly_generated_energy_peak',
    views.GenerationPeakViewSet,
    basename='quarterlygenerationpeak'
)

graph_router.register(
    r'quarterly_generated_energy_off_peak',
    views.GenerationOffPeakViewSet,
    basename='quarterlygenerationoffpeak'
)
