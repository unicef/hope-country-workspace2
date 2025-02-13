from django.conf import settings
from django.contrib.auth.models import Group, Permission


def setup_workspace_group() -> None:
    ws_group, __ = Group.objects.get_or_create(name=settings.ANALYST_GROUP_NAME)
    Group.objects.get_or_create(name=settings.NEW_USER_DEFAULT_GROUP)
    for perm in Permission.objects.filter(content_type__app_label="workspaces"):
        ws_group.permissions.add(perm)
