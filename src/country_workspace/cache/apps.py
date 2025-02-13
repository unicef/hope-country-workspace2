from django.apps import AppConfig


class Config(AppConfig):
    name = __name__.rpartition(".")[0]
    verbose_name = "Cache"

    def ready(self) -> None:
        from .manager import cache_manager

        cache_manager.init()
