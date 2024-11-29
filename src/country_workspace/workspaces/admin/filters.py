from typing import TYPE_CHECKING, Any

from django.contrib.admin import SimpleListFilter
from django.http import HttpRequest
from django.urls import reverse
from django.utils.translation import gettext as _

from adminfilters.autocomplete import AutoCompleteFilter, LinkedAutoCompleteFilter
from adminfilters.combo import ChoicesFieldComboFilter
from adminfilters.mixin import SmartFieldListFilter
from debugpy.common.util import force_str

from country_workspace.admin.job import FailedFilter
from country_workspace.models import User
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


#
# class ProgramFilter(CWLinkedAutoCompleteFilter):
#
#     def queryset(self, request: HttpRequest, queryset: "QuerySet[Beneficiary]") -> "QuerySet[Beneficiary]":
#         if self.lookup_val:
#             p = state.tenant.programs.get(pk=self.lookup_val)
#             # if request.usser.has_perm()
#             queryset = super().queryset(request, queryset).filter(batch__program=p)
#         return queryset
#
#
# class BatchFilter(CWLinkedAutoCompleteFilter):
#     def has_output(self) -> bool:
#         return bool("batch__program__exact" in self.request.GET)
#
#     def queryset(self, request: HttpRequest, queryset: "QuerySet[Beneficiary]") -> "QuerySet[Beneficiary]":
#         if self.lookup_val:
#             queryset = super().queryset(request, queryset).filter(batch=self.lookup_val)
#         return queryset
#


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


class IsValidFilter(SimpleListFilter):
    title = "Valid"
    # lookup_val = "valid"
    parameter_name = "valid"
    template = "workspace/adminfilters/combobox.html"

    def lookups(self, request, model_admin):
        return (
            ("v", _("Valid")),
            ("i", _("Invalid")),
            ("u", _("Not Verified")),
        )

    def get_title(self):
        return self.title

    def queryset(self, request, queryset):
        if self.value() == "v":
            return queryset.filter(last_checked__isnull=False).filter(errors__iexact="{}")
        elif self.value() == "i":
            return queryset.filter(last_checked__isnull=False).exclude(errors__iexact="{}")
        elif self.value() == "u":
            return queryset.filter(last_checked__isnull=True)
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


class ChoiceFilter(ChoicesFieldComboFilter):
    template = "workspace/adminfilters/combobox.html"


class WFailedFilter(FailedFilter):
    template = "workspace/adminfilters/combobox.html"


class OwnerFilter(SmartFieldListFilter):
    template = "workspace/adminfilters/combobox.html"

    def expected_parameters(self):
        return ["owner"]

    def choices(self, changelist):
        value = self.used_parameters.get(self.field.name)
        yield {
            "selected": value is None,
            "query_string": changelist.get_query_string({}, [self.field.name]),
            "display": _("All"),
        }
        for pk, username in User.objects.values_list("pk", "username"):
            selected = value is not None and force_str(pk, "utf8") in value
            yield {
                "selected": selected,
                "query_string": changelist.get_query_string({self.field.name: pk}, []),
                "display": username,
            }


class UserAutoCompleteFilter(AutoCompleteFilter):
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
        super().__init__(field, request, params, model, model_admin, field_path)

    def get_url(self) -> str:
        base_url = reverse("admin:country_workspace_user_autocomplete")
        # if self.parent_lookup_kwarg in self.request.GET:
        #     flt = self.parent_lookup_kwarg.split("__")[-2]
        #     oid = self.request.GET[self.parent_lookup_kwarg]
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
