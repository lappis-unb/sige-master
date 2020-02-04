from django.urls import path
from django.urls import include
from django.contrib import admin
from django.conf.urls import url
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import views as auth_views

from rest_framework.routers import DefaultRouter

from campi import views as campi_views
from users import views as users_views
from events import urls as events_routes
from transductors import views as energy_transductor_views

from slaves import views as slaves_views
from measurements import urls as measurements_routes

from .views import login



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
    path('rosetta/', include('rosetta.urls')),
    path('login/', login),
    path(
        'password_reset/',
        auth_views.PasswordResetView.as_view(),
        name='password_reset'
    ),
    path(
        'password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(),
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(),
        name='password_reset_confirm'
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(),
        name='password_reset_complete'
    ),
    path('', include(router.urls)),
    path('graph/', include(measurements_routes.graph_router.urls))
]
