from typing import TYPE_CHECKING

from django.urls import reverse

import pytest
from responses import RequestsMock
from testutils.perms import user_grant_permissions
from testutils.utils import select_office

from country_workspace.state import state

if TYPE_CHECKING:
    from django_webtest.pytest_plugin import MixinWithInstanceVariables
    from testutils.types import CWTestApp

    from country_workspace.workspaces.models import CountryHousehold, CountryProgram

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
def household(program):
    from testutils.factories import CountryHouseholdFactory

    return CountryHouseholdFactory(batch__program=program, batch__country_office=program.country_office)


@pytest.fixture()
def app(django_app_factory: "MixinWithInstanceVariables", mocked_responses: "RequestsMock") -> "CWTestApp":
    from testutils.factories import SuperUserFactory

    django_app = django_app_factory(csrf_checks=False)
    admin_user = SuperUserFactory(username="superuser")
    django_app.set_user(admin_user)
    django_app._user = admin_user
    yield django_app


def test_hh_changelist(app: "CWTestApp", household: "CountryHousehold") -> None:
    url = reverse("workspace:workspaces_countryhousehold_changelist")
    program: "CountryProgram" = household.program
    with select_office(app, program.country_office, program):
        res = app.get(url)
        assert res.status_code == 200, res.location
        assert f"Add {household._meta.verbose_name}" not in res.text
        # filter by program
        res = app.get(url)
        assert res.status_code == 200, res.location


def test_hh_change(app: "CWTestApp", household: "CountryHousehold") -> None:
    url = reverse("workspace:workspaces_countryhousehold_change", args=[household.pk])
    program: "CountryProgram" = household.program
    with select_office(app, program.country_office, program):
        res = app.get(url)
        assert res.status_code == 200, res.location
        res = res.forms["countryhousehold_form"].submit()
        assert res.status_code == 302, res.location


def test_hh_validate_single(app: "CWTestApp", household: "CountryHousehold") -> None:
    with select_office(app, household.country_office, household.program):
        with user_grant_permissions(app._user, ["workspaces.change_countryhousehold"], household.program):
            url = reverse("workspace:workspaces_countryhousehold_change", args=[household.pk])
            res = app.get(url)
            res = res.click("Validate")
            res = res.follow()
            assert res.status_code == 200


def test_hh_validate_program(app: "CWTestApp", household: "CountryHousehold") -> None:
    with select_office(app, household.country_office, household.program):
        with user_grant_permissions(app._user, ["workspaces.change_countryhousehold"], household.program):
            url = reverse("workspace:workspaces_countryhousehold_changelist")
            res = app.get(url)
            res.click("Validate Programme").follow()
            household.refresh_from_db()
            assert household.last_checked


def test_hh_update_single(app: "CWTestApp", household: "CountryHousehold") -> None:
    with select_office(app, household.country_office, household.program):
        with user_grant_permissions(app._user, ["workspaces.change_countryhousehold"], household.program):
            url = reverse("workspace:workspaces_countryhousehold_change", args=[household.pk])
            res = app.get(url)
            assert res.status_code == 200
