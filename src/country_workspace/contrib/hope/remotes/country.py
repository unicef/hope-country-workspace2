from typing import TYPE_CHECKING

from django import forms

from hope_flex_fields.attributes.abstract import AbstractAttributeHandler, AttributeHandlerConfig

if TYPE_CHECKING:
    from hope_flex_fields.types import Json


class HopeLookupAttribute:
    pass


class CountryAttributeHandlerConfig(AttributeHandlerConfig):
    remote_url = forms.CharField()
    cache_ttl = forms.IntegerField(initial=60)


class CountryAttributeHandler(AbstractAttributeHandler):
    config_class = CountryAttributeHandlerConfig

    def set(self, value: "Json"):
        pass

    def get(self) -> "Json":
        from country_workspace.contrib.hope.client import HopeClient

        client = HopeClient()
        results = client.get(self.config["remote_url"])
        data = []
        self.owner.strategy_config = {}
        for row in results:
            data.append((row["id"], row["name"]))
        return {"choices": data}
