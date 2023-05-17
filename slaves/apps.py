from django.apps import AppConfig


class SlavesConfig(AppConfig):
    name = "slaves"
    verbose_name = "Slave server module"
    verbose_name_plural = "Slave server module"
    api = None

    def ready(self):
        from . import api

        self.api = api
