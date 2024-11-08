from unittest.mock import Mock

from django import forms
from django.conf import settings

from constance.test.unittest import override_config
from hope_flex_fields.models import FieldDefinition
from strategy_field.utils import fqn
from testutils.factories import FieldDefinitionFactory

from country_workspace.contrib.hope.remotes.country import CountryAttributeHandler


@override_config(HOPE_API_URL=settings.HOPE_API_URL, HOPE_API_TOKEN=settings.HOPE_API_TOKEN)
def test_r_country_fetcher():
    f = CountryAttributeHandler(
        Mock(
            attrs={},
            strategy_config={
                "remote_url": "/lookups/country/",
                "cache_ttl": 60,
            },
        )
    )
    assert f.get()


@override_config(HOPE_API_URL=settings.HOPE_API_URL, HOPE_API_TOKEN=settings.HOPE_API_TOKEN)
def test_r_country():
    fd: FieldDefinition = FieldDefinitionFactory(
        name="HOPE HH Country",
        field_type=forms.ChoiceField,
        attrs={},
        attributes_strategy=fqn(CountryAttributeHandler),
        strategy_config={
            "remote_url": "/lookups/country/",
            "cache_ttl": 60,
        },
    )
    assert fd.attributes["choices"][0] == ("b902840f-68d3-40a0-b74d-0fb14096a11e", "Afghanistan")
