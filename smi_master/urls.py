"""smi_master URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
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

router = DefaultRouter()
router.register(r'campi', campi_views.CampusViewSet)
router.register(r'buildings', buildings_views.BuildingViewset)
router.register(r'slave', slaves_views.SlaveViewSet)
router.register(r'minutely_measurements', measurements_views.MinutelyMeasurementViewSet)
router.register(r'quarterly_measurements', measurements_views.QuarterlyMeasurementViewSet)
router.register(
    r'transductor_models',
    transductor_models_views.TransductorModelViewSet
)
router.register(
    r'energy_transductors',
    energy_transductor_views.EnergyTransductorViewSet
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls))
]
