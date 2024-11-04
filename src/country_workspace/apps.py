from django.apps import AppConfig


class Config(AppConfig):
    name = __name__.rpartition(".")[0]
    verbose_name = "Country Workspace"

    def ready(self) -> None:
        from hope_flex_fields.attributes.registry import attributes_registry
        from hope_flex_fields.registry import field_registry

        from .remotes.country import CountryAttributeHandler
        from .utils import flags  # noqa

        attributes_registry.register(CountryAttributeHandler)
