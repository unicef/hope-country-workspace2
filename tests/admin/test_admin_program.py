from typing import TYPE_CHECKING

from django.urls import reverse

import pytest
from django_webtest.pytest_plugin import MixinWithInstanceVariables

from country_workspace.models import User

if TYPE_CHECKING:
    from testutils.types import CWTestApp

    from country_workspace.workspaces.models import CountryProgram


@pytest.fixture()
def program():
    from testutils.factories import CountryProgramFactory

    return CountryProgramFactory()


@pytest.fixture()
def app(django_app_factory: "MixinWithInstanceVariables") -> "CWTestApp":
    django_app = django_app_factory(csrf_checks=False)
    yield django_app


def test_program_zap(app, user: "User", program: "CountryProgram"):
    base_url = reverse("admin:country_workspace_program_zap", args=[program.pk])
    app.set_user(user)
    res = app.get(base_url, expect_errors=True)
    res = res.form.submit()
    res = res.follow()
    assert res.status_code == 302
