from django.apps import AppConfig


class SlavesConfig(AppConfig):
    name = 'slaves'
    api = None

    def ready(self):
        from . import api
        self.api = api
