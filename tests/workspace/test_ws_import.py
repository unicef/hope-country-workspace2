import json
import re
from pathlib import Path

from django.urls import reverse

import pytest
from constance.test.unittest import override_config
from django_webtest import DjangoTestApp
from django_webtest.pytest_plugin import MixinWithInstanceVariables
from webtest import Upload

from country_workspace.state import state
from country_workspace.workspaces.models import CountryHousehold


@pytest.fixture
def office():
    from testutils.factories import OfficeFactory

    co = OfficeFactory()
    state.tenant = co
    return co


@pytest.fixture
def program(office, force_migrated_records, household_checker, individual_checker):
    from testutils.factories import CountryProgramFactory

    return CountryProgramFactory(
        country_office=office,
        household_checker=household_checker,
        individual_checker=individual_checker,
        household_columns="name\nid\nxx",
        individual_columns="name\nid\nxx",
    )


@pytest.fixture
def app(django_app_factory: "MixinWithInstanceVariables") -> "DjangoTestApp":
    from testutils.factories import SuperUserFactory

    django_app = django_app_factory(csrf_checks=False)
    admin_user = SuperUserFactory(username="superuser")
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


def test_import_data_rdi(force_migrated_records, app, program):
    # NOTE: This test is linked to the content of `data/rdi_one.xlsx`
    res = app.get("/").follow()
    res.forms["select-tenant"]["tenant"] = program.country_office.pk
    res.forms["select-tenant"].submit()

    url = reverse("workspace:workspaces_countryprogram_import_data", args=[program.pk])
    data = (Path(__file__).parent.parent / "data/rdi_one.xlsx").read_bytes()

    res = app.get(url)
    res.forms["import-file"]["_selected_tab"] = "rdi"
    res.forms["import-file"]["rdi-file"] = Upload("rdi_one.xlsx", data)
    res.forms["import-file"]["rdi-detail_column_label"] = "full_name"
    res = res.forms["import-file"].submit()
    assert res.status_code == 302
    assert program.households.count() == 1
    assert program.individuals.count() == 5

    hh: "CountryHousehold" = program.households.first()
    assert hh.members.count() == 5
    assert (head := hh.heads().first())
    assert head.name == "Edward Jeffrey Rogers"


@override_config(AURORA_API_URL="https://api.aurora.io")
def test_import_data_aurora(force_migrated_records, app, program, mocked_responses):
    mocked_responses.add(
        mocked_responses.GET,
        re.compile(r"https://api.aurora.io/record/.*"),
        json=json.loads((Path(__file__).parent / "aurora.json").read_text()),
        status=200,
    )
    res = app.get("/").follow()
    res.forms["select-tenant"]["tenant"] = program.country_office.pk
    res.forms["select-tenant"].submit()

    url = reverse("workspace:workspaces_countryprogram_import_data", args=[program.pk])
    res = app.get(url)
    res.forms["import-aurora"]["_selected_tab"] = "aurora"
    res = res.forms["import-aurora"].submit()
    assert res.status_code == 302
    assert program.households.count() == 2
    assert program.individuals.count() == 3

    hh = program.households.first()
    assert hh.members.count() == 2
