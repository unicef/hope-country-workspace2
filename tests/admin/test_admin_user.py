from typing import TYPE_CHECKING

from django.urls import reverse

import factory
import pytest
from django_webtest.pytest_plugin import MixinWithInstanceVariables
from testutils.perms import user_grant_permissions

from country_workspace.models import User

if TYPE_CHECKING:
    from testutils.types import CWTestApp

    from country_workspace.workspaces.models import CountryProgram


@pytest.fixture
def program():
    from testutils.factories import CountryProgramFactory

    return CountryProgramFactory()


@pytest.fixture
def app(django_app_factory: "MixinWithInstanceVariables") -> "CWTestApp":
    return django_app_factory(csrf_checks=False)


@pytest.fixture
def user(db, worker_id):
    from testutils.factories import UserFactory

    def username(instance: "User", step: int) -> str:
        return f"au{step:<03}_{worker_id}@example.com"

    return UserFactory(username=factory.LazyAttributeSequence(username))


def test_user_autocomplete(app, user: "User", program: "CountryProgram"):
    base_url = reverse("admin:country_workspace_user_autocomplete")
    res = app.get(base_url, expect_errors=True)
    app.set_user(None)
    assert res.status_code == 403

    app.set_user(user)
    res = app.get(base_url, expect_errors=True)
    assert res.json["results"] == [{"id": user.pk, "text": user.username}]

    with user_grant_permissions(user, ["workspaces.view_countryhousehold"], program):
        res = app.get(f"{base_url}?program={program.pk}", expect_errors=True)
        assert res.json["results"] == [{"id": user.pk, "text": user.username}]
