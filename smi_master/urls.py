from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from buildings import views as buildings_views
from campi import views as campi_views
from measurements import urls as measurements_routes
from slaves import views as slaves_views
from transductors import views as energy_transductor_views
from users import views as users_views

from .views import login

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
