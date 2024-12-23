from typing import Sequence

from django.contrib import admin
from django.http import HttpRequest

from adminfilters.autocomplete import AutoCompleteFilter, LinkedAutoCompleteFilter
from django_celery_boost.admin import CeleryTaskModelAdmin

from ..models import AsyncJob
from .base import BaseModelAdmin
from .filters import FailedFilter


@admin.register(AsyncJob)
class AsyncJobAdmin(CeleryTaskModelAdmin, BaseModelAdmin):
    list_display = ("program", "type", "verbose_status", "owner")
    autocomplete_fields = ("program", "owner", "batch", "content_type")
    list_filter = (
        ("program__country_office", LinkedAutoCompleteFilter.factory(parent=None)),
        ("program", LinkedAutoCompleteFilter.factory(parent="program__country_office")),
        ("owner", AutoCompleteFilter),
        "type",
        FailedFilter,
    )

    def get_readonly_fields(self, request: "HttpRequest", obj: "AsyncJob | None" = None) -> Sequence[str]:
        if obj:
            return ("program", "batch", "owner", "local_status", "type", "action", "sentry_id")
        return super().get_readonly_fields(request, obj)
