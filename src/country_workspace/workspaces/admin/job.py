from typing import Optional

from django.contrib import messages
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
        "request_timestamp",
        "completed_time",
        "type",
        "started",
        "is_queued",
        "queue_position",
        "status",
        "owner",
    )
    list_filter = (("type", ChoiceFilter),)
    search_fields = ("name",)
    exclude = ("program",)
    readonly_fields = ("type", "batch", "file", "config", "repeatable", "owner", "request_timestamp", "action")

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

    @button(label="Terminate", permission=lambda r, o, handler: handler.model_admin.has_queue_permission("queue", r, o))
    def celery_terminate(self, request: "HttpRequest", pk: str) -> "HttpResponse":  # type: ignore
        obj = self.get_object(request, pk)
        if obj.is_terminated():
            self.message_user(request, "This task  is already terminated.", messages.WARNING)
            return
        return self._celery_terminate(request, pk)

    @button(label="Queue", permission=lambda r, o, handler: handler.model_admin.has_queue_permission("queue", r, o))
    def celery_revoke(self, request: "HttpRequest", pk: str) -> "HttpResponse":  # type: ignore
        obj = self.get_object(request, pk)
        if obj.is_terminated():
            self.message_user(request, "This task is already terminated.", messages.WARNING)
            return
        return self._celery_revoke(request, pk)

    @button(label="Queue", permission=lambda r, o, handler: handler.model_admin.has_queue_permission("queue", r, o))
    def celery_queue(self, request: "HttpRequest", pk: str) -> "HttpResponse":  # type: ignore
        obj: Optional[CountryAsyncJob]
        obj = self.get_object(request, pk)
        # ctx = self.get_common_context(request, pk, title=f"Confirm queue action for {obj}")
        if obj.is_queued():
            self.message_user(request, "This has already been queued.", messages.WARNING)
            return
        if obj.is_terminated():
            self.message_user(request, "This is already terminated.", messages.WARNING)
            return
        return self._celery_queue(request, pk)
        #
        # def doit(request: "HttpRequest") -> HttpResponseRedirect:
        #     obj.queue()
        #     redirect_url = reverse(
        #         "%s:%s_%s_change" % (self.admin_site.name, obj._meta.app_label, obj._meta.model_name),
        #         args=(obj.pk,),
        #         current_app=self.admin_site.name,
        #     )
        #     return HttpResponseRedirect(redirect_url)
        #
        # return confirm_action(
        #     self,
        #     request,
        #     doit,
        #     "Do you really want to queue this task?",
        #     "Queued",
        #     extra_context=ctx,
        #     description="",
        #     template=self.queue_template or [
        #
        #         "%s/%s/%s/queue.html" % (self.admin_site.name, self.opts.app_label, self.opts.model_name),
        #         "%s/%s/queue.html" % (self.admin_site.name, self.opts.app_label),
        #         "%s/celery_boost/queue.html" % self.admin_site.name,
        #     ],
        # )
