from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from apps.accounts.urls import router as accounts_router
from apps.events.urls import router as events_router
from apps.locations.urls import router as locations_router
from apps.measurements.urls import router as measurements_router
from apps.organizations.urls import router as organizations_router
from apps.transductors.urls import router as transductors_router
from apps.unifilar_diagram.urls import router as unifilar_diagram_router

# from django.contrib.auth import views as auth_views

app_name = "api"
api_router = DefaultRouter() if settings.DEBUG else SimpleRouter()

# Estendendo o api_router principal com todos os sub-routers (APPs)
api_router.registry.extend(events_router.registry)
api_router.registry.extend(locations_router.registry)
api_router.registry.extend(measurements_router.registry)
api_router.registry.extend(organizations_router.registry)
api_router.registry.extend(transductors_router.registry)
api_router.registry.extend(unifilar_diagram_router.registry)
api_router.registry.extend(accounts_router.registry)

urlpatterns = api_router.urls
