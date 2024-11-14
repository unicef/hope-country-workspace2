from typing import TYPE_CHECKING

from django.contrib.admin.utils import quote
from django.contrib.admin.views.main import ChangeList as DjangoChangeList
from django.urls import reverse

from hope_flex_fields.models import DataChecker

from ..cache.manager import cache_manager

if TYPE_CHECKING:
    from .templatetags.workspace_list import ResultList


class WorkspaceChangeList(DjangoChangeList):
    selected_program_filter: str = ""

    def get_ordering_field(self, field_name: str) -> str:
        try:
            return super().get_ordering_field(field_name)
        except AttributeError:
            return field_name

    def get_ordering_field_columns(self) -> list[str]:
        return super().get_ordering_field_columns()

    def url_for_result(self, result: "ResultList") -> str:
        pk = getattr(result, self.pk_attname)
        return reverse(
            "%s:%s_%s_change"
            % (
                self.model_admin.admin_site.namespace,
                self.opts.app_label,
                self.opts.model_name,
            ),
            args=(quote(pk),),
            current_app=self.model_admin.admin_site.name,
        )

    def get_queryset(self, request, exclude_parameters=None):
        (
            self.filter_specs,
            self.has_filters,
            remaining_lookup_params,
            filters_may_have_duplicates,
            self.has_active_filters,
        ) = self.get_filters(request)
        key = cache_manager.build_key_from_request(request, "qs")
        if not (qs := cache_manager.get(key)):
            qs = super().get_queryset(request, exclude_parameters)
            cache_manager.set(key, qs)
        self.clear_all_filters_qs = self.get_query_string(
            new_params=remaining_lookup_params,
            remove=self.get_filters_params(),
        )
        return qs


class FlexFieldsChangeList(WorkspaceChangeList):
    checker: "DataChecker"
