from typing import TYPE_CHECKING

from django.urls import reverse

import pytest
from responses import RequestsMock
from testutils.utils import select_office

from country_workspace.state import state

if TYPE_CHECKING:
    from django_webtest.pytest_plugin import MixinWithInstanceVariables
    from testutils.types import CWTestApp

    from country_workspace.workspaces.models import CountryBatch

pytestmark = [pytest.mark.admin, pytest.mark.smoke, pytest.mark.django_db]


@pytest.fixture()
def office():
    from testutils.factories import OfficeFactory

    co = OfficeFactory()
    state.tenant = co
    yield co


@pytest.fixture()
def program(office, household_checker, individual_checker):
    from testutils.factories import CountryProgramFactory

    return CountryProgramFactory(
        household_checker=household_checker,
        individual_checker=individual_checker,
        household_columns="name\nid\nxx",
        individual_columns="name\nid\nxx",
    )


@pytest.fixture()
def batch(program):
    from testutils.factories import CountryHouseholdFactory

    hh = CountryHouseholdFactory(batch__program=program, batch__country_office=program.country_office)
    return hh.batch


@pytest.fixture()
def app(django_app_factory: "MixinWithInstanceVariables", mocked_responses: "RequestsMock") -> "CWTestApp":
    from testutils.factories import SuperUserFactory

    django_app = django_app_factory(csrf_checks=False)
    admin_user = SuperUserFactory(username="superuser")
    django_app.set_user(admin_user)
    django_app._user = admin_user
    yield django_app


def test_batch_changelist(app: "CWTestApp", batch: "CountryBatch") -> None:
    url = reverse("workspace:workspaces_countrybatch_changelist")
    with select_office(app, batch.program.country_office, batch.program):
        res = app.get(url)
        assert res.status_code == 200, res.location
        assert f"Add {batch._meta.verbose_name}" not in res.text
        res = app.get(url)
        assert res.status_code == 200, res.location


def test_batch_change(app: "CWTestApp", batch: "CountryBatch") -> None:
    url = reverse("workspace:workspaces_countrybatch_change", args=[batch.pk])
    with select_office(app, batch.program.country_office, batch.program):
        res = app.get(url)
        assert res.status_code == 200, res.location
        assert "Batches" in res.text
        res = res.forms["countrybatch_form"].submit()
        assert res.status_code == 302, res.location
