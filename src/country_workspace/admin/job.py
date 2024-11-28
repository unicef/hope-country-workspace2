from django.contrib import admin

from adminfilters.autocomplete import AutoCompleteFilter, LinkedAutoCompleteFilter
from django_celery_boost.admin import CeleryTaskModelAdmin

from ..models import AsyncJob
from .base import BaseModelAdmin


@admin.register(AsyncJob)
class AsyncJobAdmin(CeleryTaskModelAdmin, BaseModelAdmin):
    list_display = ("program", "type", "verbose_status")
    readonly_fields = ("program", "batch", "owner", "local_status")
    list_filter = (
        ("program__country_office", LinkedAutoCompleteFilter.factory(parent=None)),
        ("program", LinkedAutoCompleteFilter.factory(parent="program__country_office")),
        ("owner", AutoCompleteFilter),
    )
