import pytest
from django_webtest.pytest_plugin import MixinWithInstanceVariables
from testutils.perms import user_grant_permissions
from testutils.types import CWTestApp

from country_workspace.cache import CacheManager
from country_workspace.models import User
from country_workspace.state import state


@pytest.fixture()
def app(django_app_factory: "MixinWithInstanceVariables", user: "User") -> "CWTestApp":
    django_app = django_app_factory(csrf_checks=False)
    django_app.set_user(user)
    django_app._user = user
    yield django_app


@pytest.fixture()
def program():
    from testutils.factories import CountryProgramFactory

    return CountryProgramFactory()


@pytest.fixture
def manager():
    return CacheManager()


def test_cache_manager_init():
    pass


def test_cache_manager_build_key_from_request(app, manager, program, rf):
    request = rf.get("/")
    # with select_office(app, program.country_office, program):
    assert manager._build_key_from_request(request) == ""

    with user_grant_permissions(
        app._user, "workspaces.view_countryhousehold", country_office_or_program=program.country_office
    ):
        # with select_office(app, program.country_office, program):
        with state.set(tenant=program.country_office, program=program):
            assert manager._build_key_from_request(request) == f"afghanistan:{program.pk}::"
