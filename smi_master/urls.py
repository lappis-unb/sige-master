from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from django.conf.urls import url

from buildings import views as buildings_views
from slaves import views as slaves_views
from campi import views as campi_views
from transductors import views as energy_transductor_views
from users import views as users_views
from .views import login

from measurements import urls as measurements_routes

router = DefaultRouter()
router.register(r'campi', campi_views.CampusViewSet)
router.register(r'buildings', buildings_views.BuildingViewset)
router.register(r'slave', slaves_views.SlaveViewSet)
router.register(r'users', users_views.UserViewSet)
router.register(
    r'energy_transductors',
    energy_transductor_views.EnergyTransductorViewSet
)

router.registry.extend(measurements_routes.router.registry)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', login),
    path('', include(router.urls)),
    path('graph/', include(measurements_routes.graph_router.urls))
]
