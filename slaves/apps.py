from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SlavesConfig(AppConfig):
    name = _('slaves')
    verbose_name = _('Slave server module')
    api = None

    def ready(self):
        from . import api
        self.api = api
