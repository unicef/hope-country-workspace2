from typing import Optional, Sequence

from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.http import HttpRequest
from django.utils.translation import gettext as _

from adminfilters.autocomplete import AutoCompleteFilter, LinkedAutoCompleteFilter
from django_celery_boost.admin import CeleryTaskModelAdmin

from ..models import AsyncJob
from .base import BaseModelAdmin


class FailedFilter(SimpleListFilter):
    title = "Status"
    parameter_name = "failed"

    def lookups(self, request, model_admin):
        return (
            ("f", _("Failed")),
            ("s", _("Success")),
        )

    def get_title(self):
        return self.title

    def queryset(self, request, queryset):
        if self.value() == "s":
            return queryset.filter(sentry_id__isnull=True)
        elif self.value() == "f":
            return queryset.filter(sentry_id__isnull=False)
        return queryset

    def has_output(self):
        return True

    def html_attrs(self):
        classes = f"adminfilters  {self.__class__.__name__.lower()}"
        if self.value():
            classes += " active"

        return {
            "class": classes,
            "id": "_".join(self.expected_parameters()),
        }


@admin.register(AsyncJob)
class AsyncJobAdmin(CeleryTaskModelAdmin, BaseModelAdmin):
    list_display = ("program", "type", "verbose_status")
    autocomplete_fields = ("program", "owner")
    list_filter = (
        ("program__country_office", LinkedAutoCompleteFilter.factory(parent=None)),
        ("program", LinkedAutoCompleteFilter.factory(parent="program__country_office")),
        ("owner", AutoCompleteFilter),
        FailedFilter,
    )

    def get_readonly_fields(self, request: "HttpRequest", obj: "Optional[AsyncJob]" = None) -> Sequence[str]:
        if obj:
            return ("program", "batch", "owner", "local_status", "type", "action", "sentry_id")
        return super().get_readonly_fields(request, obj)
