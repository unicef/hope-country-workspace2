from typing import TYPE_CHECKING

from django.db.models import Model

import pytest
from django_webtest.pytest_plugin import MixinWithInstanceVariables
from testutils.factories import get_factory_for_model
from testutils.perms import user_grant_permissions

from country_workspace.cache.manager import CacheManager
from country_workspace.models import User
from country_workspace.state import state

if TYPE_CHECKING:
    from testutils.types import CWTestApp


def pytest_generate_tests(metafunc: "Metafunc") -> None:  # noqa
    import django

    from country_workspace.models import Household, Individual, Program
    from country_workspace.workspaces.models import CountryHousehold, CountryIndividual, CountryProgram

    django.setup()
    if "model" in metafunc.fixturenames:
        m2: list[Model] = []
        ids = []
        for model in (Household, Individual, CountryHousehold, CountryIndividual, Program, CountryProgram):
            name = model._meta.object_name
            full_name = f"{model._meta.app_label}.{name}"
            m2.append(model)
            ids.append(full_name)
        metafunc.parametrize("model", m2, ids=ids)


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
    m = CacheManager()
    m.init()
    return m


def test_cache_manager_init():
    pass


def test_cache_manager_build_key_from_request(app, manager, program, rf):
    request = rf.get("/")
    assert manager.build_key_from_request(request) == "view:-:-:-::"

    with user_grant_permissions(
        app._user, "workspaces.view_countryhousehold", country_office_or_program=program.country_office
    ):
        with state.set(tenant=program.country_office, program=program):
            key = manager.build_key_from_request(request)
            assert key.startswith("view:")
            assert program.country_office.slug in key


def test_invalidate(manager, program):
    manager.reset_cache_version(program=program)
    v = manager.get_cache_version(program=program)
    assert v == 1

    manager.incr_cache_version(program=program)
    v = manager.get_cache_version(program=program)
    assert v == 2

    manager.incr_cache_version(program=program)
    v = manager.get_cache_version(program=program)
    assert v == 3


def test_handlers(manager, model):
    fc = get_factory_for_model(model)
    obj = fc()
    program = getattr(obj, "program", obj)
    v1 = manager.get_cache_version(program=program)
    obj.save()
    v2 = manager.get_cache_version(program=program)
    assert v2 > v1
