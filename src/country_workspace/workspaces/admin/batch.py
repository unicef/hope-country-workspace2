from typing import TYPE_CHECKING, Optional

from django.contrib.admin import register
from django.db.models import QuerySet
from django.http import HttpRequest
from django.urls import reverse

from admin_extra_buttons.buttons import LinkButton
from admin_extra_buttons.decorators import link

from ...state import state
from ..models import CountryBatch
from ..options import WorkspaceModelAdmin
from ..sites import workspace
from .filters import ChoiceFilter, CWLinkedAutoCompleteFilter, UserAutoCompleteFilter
from .hh_ind import SelectedProgramMixin

if TYPE_CHECKING:
    pass


class ProgramBatchFilter(CWLinkedAutoCompleteFilter):

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet:
        if self.lookup_val:
            p = state.tenant.programs.get(pk=self.lookup_val)
            queryset = super().queryset(request, queryset).filter(program=p)
        return queryset


@register(CountryBatch, site=workspace)
class CountryBatchAdmin(SelectedProgramMixin, WorkspaceModelAdmin):
    list_display = ["import_date", "name", "imported_by", "source"]
    search_fields = ("label",)
    change_list_template = "workspace/change_list.html"
    change_form_template = "workspace/change_form.html"
    ordering = ("name",)
    list_filter = (("source", ChoiceFilter), ("imported_by", UserAutoCompleteFilter))
    readonly_fields = fields = ("name", "source")

    def get_search_results(self, request, queryset, search_term):
        queryset = self.model.objects.filter(program=state.program)
        return queryset, False

    def get_queryset(self, request: HttpRequest) -> "QuerySet[CountryBatch]":
        return (
            super()
            .get_queryset(request)
            .select_related("program", "country_office")
            .filter(country_office=state.tenant, program=state.program)
        )

    def has_add_permission(self, request: HttpRequest, obj: Optional[CountryBatch] = None) -> bool:
        return False

    @link(change_list=False)
    def imported_records(self, btn: LinkButton) -> None:
        base = reverse("workspace:workspaces_countryhousehold_changelist")
        obj = btn.context["original"]
        btn.href = f"{base}?batch__exact={obj.pk}"
