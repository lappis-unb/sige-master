from django.apps import AppConfig


class TransductorsConfig(AppConfig):
    name = "transductors"
    verbose_name = "Meters module"
    api = None

    def ready(self):
        from . import api

        self.api = api
