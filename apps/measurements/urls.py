from rest_framework import routers

from apps.measurements.views import (
    CumulativeCreateViewSet,
    CumulativeMeasurementViewSet,
    InstantaneousCreateViewSet,
    InstantMeasurementViewSet,
    RealTimeMeasurementViewSet,
)

app_name = "minutely_measurements"

router = routers.DefaultRouter()

router.register(r"instantaneous-measurements", InstantMeasurementViewSet)
router.register(r"instantaneous-create", InstantaneousCreateViewSet, basename="instantaneous-create")
router.register(r"cumulative-measurements", CumulativeMeasurementViewSet)
router.register(r"cumulative-create", CumulativeCreateViewSet, basename="cumulative-create")
router.register(r"realtime-measurements", RealTimeMeasurementViewSet, basename="realtime-measurements")


# graph_router = routers.DefaultRouter()
# graph_router.register(r"minutely-threephase-voltage", VoltageThreePhaseViewSet, basename="minutelyvoltage")
# graph_router.register(r"minutely-threephase-current", CurrentThreePhaseViewSet, basename="minutelycurrent")
# graph_router.register(r"minutely-frequency", FrequencyViewSet, basename="minutelyfrequency")
# graph_router.register(r"minutely-power-factor", MinutelyPowerFactorThreePhaseViewSet, basename="minutelypowerfactor")
# graph_router.register(r"minutely-dht-voltage", MinutelyDHTVoltageThreePhaseViewSet, basename="minutelydhtvoltage")
# graph_router.register(r"minutely-dht-current", MinutelyDHTCurrentThreePhaseViewSet, basename="minutelydhtcurrent")
# graph_router.register(r"quarterly-daily-consumption", DailyConsumptionViewSet, basename="quarterlydailyconsumption")
# graph_router.register(r"consumption-curve", ConsumptionCurveViewSet, basename="consumptioncurve")
# graph_router.register(r"cost-consumption", CostConsumptionViewSet, basename="costconsumption")
# graph_router.register(r"quarterly-total-generation", TotalGenerationViewSet, basename="quarterlytotalgeneration")
# graph_router.register(r"quarterly-total-consumption", TotalConsumptionViewSet, basename="quarterlytotalconsumption")
# graph_router.register(r"minutely-active-power", MinutelyActivePowerThreePhaseViewSet, basename="minutelyactivepower")

# graph_router.register(
#     r"minutely-reactive-power", MinutelyReactivePowerThreePhaseViewSet, basename="minutelyreactivepower"
# )
# graph_router.register(
#     r"minutely-apparent-power", MinutelyApparentPowerThreePhaseViewSet, basename="minutelyapparentpower"
# )
# graph_router.register(
#     r"minutely-total-active-power", MinutelyTotalActivePowerViewSet, basename="minutelytotalactivepower"
# )
# graph_router.register(
#     r"minutely-total-reactive-power", MinutelyTotalReactivePowerViewSet, basename="minutelytotalreactivepower"
# )
# graph_router.register(
#     r"minutely-total-apparent-power", MinutelyTotalApparentPowerViewSet, basename="minutelytotalapparentpower"
# )
# graph_router.register(
#     r"minutely-total-power-factor", MinutelyTotalPowerFactorViewSet, basename="minutelytotalpowerfactor"
# )
# graph_router.register(
#     r"quarterly-total-inductive-power", TotalInductivePowerViewSet, basename="quarterlytotalinductivepower"
# )
# graph_router.register(
#     r"quarterly-total-capacitive-power", TotalCapacitivePowerViewSet, basename="quarterlytotalcapacitivepower"
# )
