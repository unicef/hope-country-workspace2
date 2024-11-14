from pathlib import Path
from unittest.mock import Mock

from django import forms
from django.conf import settings

import vcr
from constance.test.unittest import override_config
from hope_flex_fields.models import FieldDefinition
from strategy_field.utils import fqn
from testutils.factories import FieldDefinitionFactory
from vcr.record_mode import RecordMode

from country_workspace.contrib.hope.remotes.country import CountryAttributeHandler

my_vcr = vcr.VCR(
    filter_headers=["authorization"],
    record_mode=RecordMode.ONCE,
    match_on=("path",),
)


@override_config(HOPE_API_URL=settings.HOPE_API_URL, HOPE_API_TOKEN=settings.HOPE_API_TOKEN)
def test_r_country_fetcher():
    with my_vcr.use_cassette(Path(__file__).parent / "country.yaml"):
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
    with my_vcr.use_cassette(Path(__file__).parent / "country.yaml"):
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
