from typing import Any

from django.conf import settings
from django.contrib.auth.models import Group, User

from constance import config


def save_to_group(user: User | None = None, **kwargs: Any) -> dict[str, Any]:
    if user:
        grp = Group.objects.get(name=config.NEW_USER_DEFAULT_GROUP)
        user.groups.add(grp)
    return {}


def set_superusers(user: User | None = None, is_new: bool = False, **kwargs: Any) -> dict[str, Any]:
    if user and is_new and user.email in settings.SUPERUSERS:
        user.is_superuser = True
        user.save()
    return {}
