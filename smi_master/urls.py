from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.utils.translation import gettext_lazy as _
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter

from campi import urls as campi_routes
from events import urls as events_routes
from groups import urls as groups_routes
from measurements import urls as measurements_routes
from measurements.views import MeasurementResults
from slaves import views as slaves_views
from transductors import urls as transductors_routes
from unifilar_diagram import urls as unifilar_diagram_routes
from users import views as users_views

from .views import login

router = DefaultRouter()
router.register(r"slave", slaves_views.SlaveViewSet)
router.register(r"users", users_views.UserViewSet)

router.registry.extend(measurements_routes.router.registry)
router.registry.extend(events_routes.router.registry)
router.registry.extend(groups_routes.router.registry)
router.registry.extend(transductors_routes.router.registry)
router.registry.extend(unifilar_diagram_routes.router.registry)

router.registry.extend(campi_routes.router.registry)

admin.site.site_header = _("SMI Site Administration")
admin.site.site_title = _("Energy monitoring system")

urlpatterns = [
    path("docs/", include_docs_urls(title="My API title")),
    path("admin/", admin.site.urls),
    path("login/", login),
    path("password_reset/validate_token/", users_views.PasswordTokenVerificationView.as_view()),
    path("password_reset/", include("django_rest_passwordreset.urls", namespace="password_reset")),
    path("csv-export/", MeasurementResults.mount_csv_measurement),
    path("graph/", include(measurements_routes.graph_router.urls)),
    path("", include(router.urls)),
    path("", include("campi.urls")),
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
