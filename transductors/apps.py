from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TransductorsConfig(AppConfig):
    name = 'transductors'
    verbose_name = _('Meters module')
    api = None

    def ready(self):
        from . import api
        self.api = api
