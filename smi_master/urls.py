from django.urls import path
from django.urls import include
from django.contrib import admin
from django.conf.urls import url, include
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import views as auth_views

from rest_framework.routers import DefaultRouter

from campi import views as campi_views
from users import views as users_views
from events import urls as events_routes
from transductors import views as energy_transductor_views
from measurements.views import MeasurementResults

from slaves import views as slaves_views
from measurements import urls as measurements_routes
from events import urls as events_routes
from groups import urls as groups_routes
from unifilar_diagram import urls as unifilar_diagram_routes

from transductors import urls as transductors_routes

from .views import login

router = DefaultRouter()
router.register(r'campi', campi_views.CampusViewSet)
router.register(r'slave', slaves_views.SlaveViewSet)
router.register(r'users', users_views.UserViewSet)

router.registry.extend(measurements_routes.router.registry)
router.registry.extend(events_routes.router.registry)
router.registry.extend(groups_routes.router.registry)
router.registry.extend(transductors_routes.router.registry)
router.registry.extend(unifilar_diagram_routes.router.registry)

# django-admin custom titles
# admin.site.index_title = _('')
admin.site.site_header = _('SMI Site Administration')
admin.site.site_title = _('Energy monitoring system')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('rosetta/', include('rosetta.urls')),
    path('login/', login),
    path('password_reset/validate_token/', 
        users_views.PasswordTokenVerificationView.as_view()),
    path('password_reset/', 
        include('django_rest_passwordreset.urls', namespace='password_reset')),
    path('csv-export/', MeasurementResults.mount_csv_measurement),
    path('', include(router.urls)),
    path('graph/', include(measurements_routes.graph_router.urls))
]

"""
    The password_reset/ actually adds two routes: 
    
    POST password_reset/reset_password/ 
    Path to get the email with the link to reset the password, where the user
    need to send the email param in req body

    &&
    
    POST password_reset/confirm/ 
    Path to reset the password, where the user need to send the received token
    and the new password.
"""