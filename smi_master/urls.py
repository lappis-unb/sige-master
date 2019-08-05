from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from django.urls import path, include
from django.conf.urls import url

from buildings import views as buildings_views
from slaves import views as slaves_views
from campi import views as campi_views
from measurements import views as measurements_views
from transductor_models import views as transductor_models_views
from transductors import views as energy_transductor_views
from users import views as users_views
from .views import login

router = DefaultRouter()
router.register(r'campi', campi_views.CampusViewSet)
router.register(r'buildings', buildings_views.BuildingViewset)
router.register(r'slave', slaves_views.SlaveViewSet)
router.register(r'users', users_views.UserViewSet)
router.register(r'minutely_measurements',
                measurements_views.MinutelyMeasurementViewSet)
router.register(r'quarterly_measurements',
                measurements_views.QuarterlyMeasurementViewSet)
router.register(r'monthly_measurements',
                measurements_views.MonthlyMeasurementViewSet)
router.register(
    r'transductor_models',
    transductor_models_views.TransductorModelViewSet
)
router.register(
    r'energy_transductors',
    energy_transductor_views.EnergyTransductorViewSet
)

single_router = DefaultRouter()

single_router.register(
    r'minutely_voltage',
    measurements_views.MinutelyVoltageThreePhaseViewSet,
    basename='minutelyvoltage'
)

single_router.register(
    r'minutely_current',
    measurements_views.MinutelyCurrentThreePhaseViewSet,
    basename='minutelycurrent'
)

single_router.register(
    r'minutely_active_power',
    measurements_views.MinutelyActivePowerThreePhaseViewSet,
    basename='minutelyactivepower'
)

single_router.register(
    r'minutely_reactive_power',
    measurements_views.MinutelyReactivePowerThreePhaseViewSet,
    basename='minutelyreactivepower'
)

single_router.register(
    r'minutely_apparent_power',
    measurements_views.MinutelyApparentPowerThreePhaseViewSet,
    basename='minutelyapparentpower'
)

single_router.register(
    r'minutely_power_factor',
    measurements_views.MinutelyPowerFactorThreePhaseViewSet,
    basename='minutelypowerfactor'
)

single_router.register(
    r'minutely_dht_voltage',
    measurements_views.MinutelyDHTVoltageThreePhaseViewSet,
    basename='minutelydhtvoltage'
)

single_router.register(
    r'minutely_dht_current',
    measurements_views.MinutelyDHTCurrentThreePhaseViewSet,
    basename='minutelydhtcurrent'
)

single_router.register(
    r'minutely_frequency',
    measurements_views.MinutelyFrequencyViewSet,
    basename='minutelyfrequency'
)

single_router.register(
    r'minutely_total_active_power',
    measurements_views.MinutelyTotalActivePowerViewSet,
    basename='minutelytotalactivepower'
)

single_router.register(
    r'minutely_total_reactive_power',
    measurements_views.MinutelyTotalReactivePowerViewSet,
    basename='minutelytotalreactivepower'
)

single_router.register(
    r'minutely_total_apparent_power',
    measurements_views.MinutelyTotalApparentPowerViewSet,
    basename='minutelytotalapparentpower'
)

single_router.register(
    r'minutely_total_power_factor',
    measurements_views.MinutelyTotalPowerFactorViewSet,
    basename='minutelytotalpowerfactor'
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', login),
    path('', include(router.urls)),
    path('chart/', include(single_router.urls)),
]
