from django.apps import AppConfig


class TransductorModelConfig(AppConfig):
    name = 'transductor_models'
    api = None

    def ready(self):
        from . import api
        self.api = api
