from typing import TYPE_CHECKING

import pytest
from django.urls import reverse
from testutils.perms import user_grant_permissions
from testutils.utils import select_office

from country_workspace.state import state

if TYPE_CHECKING:
    from django_webtest.pytest_plugin import MixinWithInstanceVariables
    from testutils.types import CWTestApp

    from country_workspace.models import CountryHousehold, User

pytestmark = [pytest.mark.security, pytest.mark.django_db]


@pytest.fixture
def office():
    from testutils.factories import OfficeFactory

    co = OfficeFactory()
    state.tenant = co
    return co


@pytest.fixture
def program(office, household_checker, individual_checker):
    from testutils.factories import CountryProgramFactory

    return CountryProgramFactory(
        household_checker=household_checker,
        individual_checker=individual_checker,
        household_columns="name\nid\nxx",
        individual_columns="name\nid\nxx",
    )


@pytest.fixture
def household(program):
    from testutils.factories import CountryHouseholdFactory

    return CountryHouseholdFactory(batch__program=program, batch__country_office=program.country_office)


@pytest.fixture
def household2() -> "CountryHousehold":
    from testutils.factories import BatchFactory, CountryHouseholdFactory

    b = BatchFactory()
    return CountryHouseholdFactory(batch=b)


@pytest.fixture
def app(django_app_factory: "MixinWithInstanceVariables", user: "User") -> "CWTestApp":
    django_app = django_app_factory(csrf_checks=False)
    django_app.set_user(user)
    django_app._user = user
    return django_app


def pytest_generate_tests(metafunc: "Metafunc") -> None:  # noqa
    if "target" in metafunc.fixturenames:
        from testutils.factories import CountryBatchFactory, CountryHouseholdFactory, CountryIndividualFactory

        targets = [
            CountryHouseholdFactory,
            CountryIndividualFactory,
            CountryBatchFactory,
        ]
        ids = ["CountryHousehold", "CountryIndividual", "CountryBatch"]
        metafunc.parametrize("target", targets, ids=ids)


def test_user_no_permissions(db, user, target):
    t = target()
    assert not user.has_perm("workspaces.view_countryhousehold", t)
    assert not user.has_perm("workspaces.view_countryhousehold", t.program)
    assert not user.has_perm("workspaces.view_countryhousehold", t.country_office)


def test_grant_role_is_not_global(user, target):
    t = target()
    with user_grant_permissions(user, ["workspaces.view_countryhousehold"], t.program.country_office):
        assert user.get_all_permissions(t.country_office) == {"workspaces.view_countryhousehold"}
        assert user.get_all_permissions() == set()


def test_user_grant_for_office(user, target, household2: "CountryHousehold", program):
    t = target()
    with user_grant_permissions(user, ["workspaces.view_countryhousehold"], t.program.country_office):
        assert user.has_perm("workspaces.view_countryhousehold", t.country_office)
        assert user.has_perm("workspaces.view_countryhousehold", t.program)

        assert not user.has_perm("workspaces.view_countryhousehold", program)
        assert not user.has_perm("workspaces.view_countryhousehold", household2.program.country_office)
        assert not user.has_perm("workspaces.view_countryhousehold", household2.program)


def test_user_no_permissions_program(db, user, program):
    assert not user.has_perm("workspaces.view_countryhousehold", program)
    assert not user.has_perm("workspaces.view_countryhousehold", program.country_office)


def test_grant_role_is_not_global_program(user, program):
    with user_grant_permissions(user, ["workspaces.view_countryhousehold"], program.country_office):
        assert user.get_all_permissions(program.country_office) == {"workspaces.view_countryhousehold"}
        assert user.get_all_permissions() == set()


def test_user_grant_for_office_program(user, household2: "CountryHousehold", program):
    with user_grant_permissions(user, ["workspaces.view_countryhousehold"], program.country_office):
        assert user.has_perm("workspaces.view_countryhousehold", program.country_office)
        assert user.has_perm("workspaces.view_countryhousehold", program)

        assert not user.has_perm("workspaces.view_countryhousehold", household2.program.country_office)
        assert not user.has_perm("workspaces.view_countryhousehold", household2.program)


def test_hh_office_security(app: "CWTestApp", household: "CountryHousehold", household2: "CountryHousehold") -> None:
    base_url = reverse("workspace:workspaces_countryhousehold_changelist")
    with user_grant_permissions(app._user, ["workspaces.view_countryhousehold"], household.country_office):
        app.get("/")
        with select_office(app, household.country_office):
            app.get(base_url)


def test_hh_program_security(app: "CWTestApp", household: "CountryHousehold", household2: "CountryHousehold") -> None:
    base_url = reverse("workspace:workspaces_countryhousehold_changelist")
    with user_grant_permissions(app._user, ["workspaces.view_countryhousehold"], household.program):
        with select_office(app, household.country_office):
            app.get(base_url)
