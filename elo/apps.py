from django.apps import AppConfig


class EloConfig(AppConfig):
    name = 'elo'

    def ready(self):
        from .cache_warmer import start_cache_warmer

        start_cache_warmer()
