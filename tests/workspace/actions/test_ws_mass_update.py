from typing import TYPE_CHECKING

import pytest
from django.urls import reverse
from pytest_django.fixtures import SettingsWrapper
from testutils.utils import select_office

from country_workspace.state import state
from country_workspace.workspaces.admin.cleaners.mass_update import mass_update_impl

if TYPE_CHECKING:
    from django_webtest import DjangoTestApp
    from django_webtest.pytest_plugin import MixinWithInstanceVariables

    from country_workspace.models import AsyncJob
    from country_workspace.workspaces.models import CountryHousehold

pytestmark = [pytest.mark.admin, pytest.mark.smoke, pytest.mark.django_db]


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
        household_columns="__str__\nid\nxx",
        individual_columns="__str__\nid\nxx",
    )


@pytest.fixture
def household(program):
    from testutils.factories import CountryHouseholdFactory

    return CountryHouseholdFactory(batch__program=program, batch__country_office=program.country_office)


@pytest.fixture
def app(
    django_app_factory: "MixinWithInstanceVariables",
    settings: SettingsWrapper,
) -> "DjangoTestApp":
    from testutils.factories import SuperUserFactory

    django_app = django_app_factory(csrf_checks=False)
    admin_user = SuperUserFactory(username="superuser")
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


def test_mass_update_impl(household):
    from country_workspace.models import Household

    mass_update_impl(Household.objects.all(), {"address": ("djangoformsfieldsfield_set_lambda", "__NEW VALUE__")})

    household.refresh_from_db()
    assert household.flex_fields["address"] == "__NEW VALUE__"


def test_mass_update(app: "DjangoTestApp", household: "CountryHousehold") -> None:
    url = reverse("workspace:workspaces_countryhousehold_changelist")
    with select_office(app, household.country_office, household.program):
        res = app.get(url)
        form = res.forms["changelist-form"]
        form["action"] = "mass_update"
        form.set("_selected_action", True)
        res = form.submit()

        form = res.forms["mass-update-form"]
        form["flex_fields__address_0"].select(text="set")
        form["flex_fields__address_1"] = "__NEW VALUE__"
        res = form.submit("_apply")

        job: "AsyncJob" = household.program.jobs.first()
        assert job is not None

        household.refresh_from_db()
        assert household.flex_fields["address"] == "__NEW VALUE__"
