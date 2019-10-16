from django.apps import AppConfig


class TransductorsConfig(AppConfig):
    name = 'transductors'
    api = None

    def ready(self):
        from . import api
        self.api = api
