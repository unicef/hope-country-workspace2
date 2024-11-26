from django.contrib.admin import register
from django.http import HttpRequest

from django_celery_boost.admin import CeleryTaskModelAdmin

from ..filters import ChoiceFilter
from ..models import CountryAsyncJob
from ..options import WorkspaceModelAdmin
from ..sites import workspace


@register(CountryAsyncJob, site=workspace)
class CountryJobAdmin(CeleryTaskModelAdmin, WorkspaceModelAdmin):
    queue_template = "workspace/celery_boost/queue.html"

    list_display = (
        "type",
        "started",
        "is_queued",
        "queue_position",
        "status",
    )
    list_filter = (("type", ChoiceFilter),)
    search_fields = ("name",)
    exclude = (
        "program",
        "action",
    )
    readonly_fields = ("type", "batch", "file", "config")

    def has_add_permission(self, request: "HttpRequest") -> bool:
        return False

    def has_delete_permission(self, request: "HttpRequest", obj: "CountryAsyncJob|None" = None) -> bool:
        return False

    def status(self, obj: "CountryAsyncJob|None") -> str:
        return obj.task_info["status"]
