from typing import TYPE_CHECKING

from django.urls import reverse

import pytest
from django_webtest.pytest_plugin import MixinWithInstanceVariables

from country_workspace.models import User

if TYPE_CHECKING:
    from testutils.types import CWTestApp

    from country_workspace.workspaces.models import CountryIndividual


@pytest.fixture()
def program():
    from testutils.factories import CountryProgramFactory

    return CountryProgramFactory()


@pytest.fixture()
def individual():
    from testutils.factories import CountryIndividualFactory

    return CountryIndividualFactory()


@pytest.fixture()
def app(django_app_factory: "MixinWithInstanceVariables", admin_user: "User") -> "CWTestApp":
    django_app = django_app_factory(csrf_checks=False)
    django_app.set_user(admin_user)
    yield django_app


def test_individual_changelist(app, individual: "CountryIndividual"):
    base_url = reverse("admin:country_workspace_individual_changelist")
    params = (
        f"batch__country_office__exact={individual.program.country_office.pk}"
        f"&batch__program__exact={individual.program.pk}"
    )
    res = app.get(f"{base_url}?{params}")
    assert res.status_code == 200
    res = res.click(individual.name)
    assert res.status_code == 200


@pytest.mark.parametrize("valid", ["v", "i", "u"])
def test_individual_filter_by_valid(app, individual: "CountryIndividual", valid):
    base_url = reverse("admin:country_workspace_individual_changelist")
    res = app.get(f"{base_url}?valid={valid}")
    assert res.status_code == 200
