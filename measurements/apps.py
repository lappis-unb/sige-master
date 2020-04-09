from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MeasurementsConfig(AppConfig):
    name = _('measurements')
    verbose_name = _('Measurements module')
