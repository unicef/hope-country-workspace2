from typing import TYPE_CHECKING, Any

from django.http import HttpRequest
from django.urls import reverse

from adminfilters.autocomplete import AutoCompleteFilter, LinkedAutoCompleteFilter
from adminfilters.combo import ChoicesFieldComboFilter

from country_workspace.admin.filters import IsValidFilter
from country_workspace.admin.job import FailedFilter
from country_workspace.state import state

if TYPE_CHECKING:
    from django.contrib.admin import ModelAdmin
    from django.db.models import Model, QuerySet

    from country_workspace.types import Beneficiary


class CWLinkedAutoCompleteFilter(LinkedAutoCompleteFilter):
    parent_lookup_kwarg: str
    template = "workspace/adminfilters/autocomplete.html"

    def __init__(
        self,
        field: Any,
        request: "HttpRequest",
        params: dict[str, Any],
        model: "Model",
        model_admin: "ModelAdmin",
        field_path: str,
    ):
        self.dependants = []
        if self.parent and not self.parent_lookup_kwarg:
            self.parent_lookup_kwarg = f"{self.parent}__exact"
        super().__init__(field, request, params, model, model_admin, field_path)
        for pos, entry in enumerate(model_admin.list_filter):
            if isinstance(entry, (list, tuple)):
                if (
                    len(entry) == 2
                    and entry[0] != self.field_path
                    and entry[1].__name__ == type(self).__name__
                    and entry[1].parent == self.field_path
                ):
                    kwarg = f"{entry[0]}__exact"
                    if entry[1].parent:
                        if kwarg not in self.dependants:
                            self.dependants.extend(entry[1].dependants)
                            self.dependants.append(kwarg)

    def get_url(self) -> str:
        url = reverse("%s:autocomplete" % self.admin_site.name)
        if self.parent_lookup_kwarg in self.request.GET:
            flt = self.parent_lookup_kwarg.split("__")[-2]
            oid = self.request.GET[self.parent_lookup_kwarg]
            return f"{url}?{flt}={oid}"
        return url

    def html_attrs(self):
        classes = f"adminfilters  {self.__class__.__name__.lower()}"
        if self.error_message:
            classes += " error"
        if self.lookup_val:
            classes += " active"

        return {
            "class": classes,
            "id": "_".join(self.expected_parameters()),
        }


class HouseholdFilter(CWLinkedAutoCompleteFilter):
    fk_name = "name"

    def get_url(self) -> str:
        url = reverse("%s:autocomplete" % self.admin_site.namespace)
        return url

    def queryset(self, request: HttpRequest, queryset: "QuerySet[Beneficiary]") -> "QuerySet[Beneficiary]":
        qs = super().queryset(request, queryset)
        if oid := state.program:
            qs = qs.filter(batch__program__exact=oid)
        else:
            qs = qs.none()
        return qs


class WIsValidFilter(IsValidFilter):
    template = "workspace/adminfilters/combobox.html"


class ChoiceFilter(ChoicesFieldComboFilter):
    template = "workspace/adminfilters/combobox.html"


class WFailedFilter(FailedFilter):
    template = "workspace/adminfilters/combobox.html"


class UserAutoCompleteFilter(AutoCompleteFilter):
    template = "workspace/adminfilters/autocomplete.html"

    def get_url(self) -> str:
        base_url = reverse("admin:country_workspace_user_autocomplete")
        url = f"{base_url}?program={state.program.pk}"
        return url

    def html_attrs(self):
        classes = f"adminfilters  {self.__class__.__name__.lower()}"
        if self.error_message:
            classes += " error"
        if self.lookup_val:
            classes += " active"

        return {
            "class": classes,
            "id": "_".join(self.expected_parameters()),
        }
