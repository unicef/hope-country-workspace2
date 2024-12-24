from typing import TYPE_CHECKING, Any

import factory
import pytest
from constance.test.unittest import override_config

from country_workspace.models import User
from country_workspace.social.pipeline import save_to_group, set_superusers

if TYPE_CHECKING:
    from django.contrib.auth.models import Group


@pytest.fixture
def group(db: Any) -> None:
    from testutils.factories import GroupFactory

    GroupFactory(name="demo")


@pytest.fixture
def user(db, worker_id):
    from testutils.factories import UserFactory

    def username(instance: "User", step: int) -> str:
        return f"user_{step:<03}_{worker_id}@example.com"

    return UserFactory(username=factory.LazyAttributeSequence(username), is_superuser=False)


@override_config(NEW_USER_DEFAULT_GROUP="demo")  # type: ignore[misc]
def test_save_to_group(group: "Group", user: "User") -> None:
    save_to_group(user)
    assert user.groups.first().name == "demo"
    assert save_to_group(None) == {}


def test_set_superusers(user: User, settings) -> None:
    settings.SUPERUSERS = [user.email]
    set_superusers(user, is_new=True)
    user.refresh_from_db()
    assert user.is_superuser


def test_set_superusers_no_change_existing(user: User, settings) -> None:
    settings.SUPERUSERS = [user.username]
    set_superusers(user)
    user.refresh_from_db()
    assert not user.is_superuser
