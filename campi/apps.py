from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CampiConfig(AppConfig):
    name = _('campi')
    verbose_name = _('Campi module')
