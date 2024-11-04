from typing import TYPE_CHECKING

from django import forms

from hope_flex_fields.attributes.abstract import AbstractAttributeHandler, AttributeHandlerConfig

from country_workspace.sync.client import HopeClient

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
        client = HopeClient()
        results = client.get(self.config["remote_url"])
        data = []
        for row in results:
            data.append(row)
            print(111.1, 111111, row)
        return data
