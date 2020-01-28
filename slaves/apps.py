from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SlavesConfig(AppConfig):
    name = 'slaves'
    verbose_name = _('Slave servers module')
    api = None

    def ready(self):
        from . import api
        self.api = api
