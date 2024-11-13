import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class Config(AppConfig):
    name = __name__.rpartition(".")[0]

    # def ready(self) -> None:
    # from .cache import cache_manager
    # cache_manager.init()
