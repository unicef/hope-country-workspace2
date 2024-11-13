from django.apps import AppConfig

from .geo import Admin1Choice, Admin2Choice, Admin3Choice, Admin4Choice, CountryChoice


class Config(AppConfig):
    name = __name__.rpartition(".")[0]
    verbose_name = "Country Workspace"

    def ready(self) -> None:
        from hope_flex_fields.attributes.registry import attributes_registry
        from hope_flex_fields.registry import field_registry

        from .remotes.country import CountryAttributeHandler

        attributes_registry.register(CountryAttributeHandler)
        field_registry.register(CountryChoice)
        field_registry.register(Admin1Choice)
        field_registry.register(Admin2Choice)
        field_registry.register(Admin3Choice)
        field_registry.register(Admin4Choice)
