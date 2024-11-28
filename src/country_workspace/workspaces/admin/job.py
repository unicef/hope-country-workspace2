from django.contrib.admin import register
from django.http import HttpRequest, HttpResponse

from admin_extra_buttons.decorators import button
from django_celery_boost.admin import CeleryTaskModelAdmin

from ..filters import ChoiceFilter
from ..models import CountryAsyncJob
from ..options import WorkspaceModelAdmin
from ..sites import workspace


@register(CountryAsyncJob, site=workspace)
class CountryJobAdmin(CeleryTaskModelAdmin, WorkspaceModelAdmin):
    queue_template = "workspace/celery_boost/queue.html"

    list_display = (
        "datetime_queued",
        "completed_time",
        "type",
        "started",
        "queue_position",
        "status",
        "owner",
    )
    list_filter = (("type", ChoiceFilter),)
    search_fields = ("name",)
    fields = ("description",)
    # exclude = ("program", "config", "batch", "curr_async_result_id", "last_async_result_id")
    # readonly_fields = ("type",  "file", "repeatable", "owner", "datetime_queued", "action")

    def has_add_permission(self, request: "HttpRequest") -> bool:
        return False

    def has_delete_permission(self, request: "HttpRequest", obj: "CountryAsyncJob|None" = None) -> bool:
        return False

    def status(self, obj: "CountryAsyncJob|None") -> str:
        return obj.task_status

    def completed_time(self, obj: "CountryAsyncJob|None") -> str:
        return obj.task_info["completed_at"]

    @button(label="Check", permission=lambda r, o, handler: handler.model_admin.has_queue_permission("queue", r, o))
    def celery_check(self, request: "HttpRequest", pk: str) -> "HttpResponse":  # type: ignore
        obj = self.get_object(request, pk)
        obj.check()
