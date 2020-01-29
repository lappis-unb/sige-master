from django.urls import path
from django.urls import include
from django.contrib import admin
from django.conf.urls import url
from django.utils.translation import gettext_lazy as _

from rest_framework.routers import DefaultRouter

from .views import login
from campi import views as campi_views
from users import views as users_views
from slaves import views as slaves_views
from transductors import views as energy_transductor_views
from measurements import urls as measurements_routes
from events import urls as events_routes


router = DefaultRouter()
router.register(r'campi', campi_views.CampusViewSet)
router.register(r'slave', slaves_views.SlaveViewSet)
router.register(r'users', users_views.UserViewSet)
router.register(
    r'energy-transductors',
    energy_transductor_views.EnergyTransductorViewSet
)

router.registry.extend(measurements_routes.router.registry)
router.registry.extend(events_routes.router.registry)

# django-admin custom titles
# admin.site.index_title = _('')
admin.site.site_header = _('SMI Site Administration')
admin.site.site_title = _('Energy monitoring system')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', login),
    path('', include(router.urls)),
    path('graph/', include(measurements_routes.graph_router.urls))
]
