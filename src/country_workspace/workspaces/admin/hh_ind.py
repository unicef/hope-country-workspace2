from typing import TYPE_CHECKING, Any, Optional

from django.contrib import messages
from django.contrib.admin.utils import unquote
from django.core.exceptions import PermissionDenied
from django.db.models import Model, QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext as _

from admin_extra_buttons.decorators import button
from adminfilters.mixin import AdminAutoCompleteSearchMixin
from hope_flex_fields.models import DataChecker

from ...state import state
from ..options import WorkspaceModelAdmin
from .cleaners import actions

if TYPE_CHECKING:
    from hope_flex_fields.forms import FlexForm

    from ...models.base import Validable
    from ...types import Beneficiary
    from .program import CountryProgram


class SelectedProgramMixin(WorkspaceModelAdmin):

    def get_selected_program(
        self, request: HttpRequest, obj: "Optional[Validable]" = None
    ) -> "tuple[str|None, CountryProgram | None]":
        return state.program

    def get_checker(self, request: HttpRequest, obj: "Optional[Beneficiary]" = None) -> "DataChecker":
        if p := state.program:
            checker = p.get_checker_for(self.model)
        else:
            checker = None
        return checker

    def delete_queryset(self, request: HttpRequest, queryset: "QuerySet[Beneficiary]") -> None:
        queryset.filter().delete()

    def delete_model(self, request: HttpRequest, obj: "Beneficiary") -> None:
        super().delete_model(request, obj)


# def etag_func(request: HttpRequest, *args, **kwargs):
#
#     return cache_manager.build_key_from_request(request)
#
#
# def last_modified_func(request: HttpRequest, *args, **kwargs):
#     return now() + timedelta(days=-10)


class BeneficiaryBaseAdmin(AdminAutoCompleteSearchMixin, SelectedProgramMixin, WorkspaceModelAdmin):
    actions = [
        actions.validate_records,
        actions.mass_update,
        actions.regex_update,
        actions.bulk_update_export,
        actions.calculate_checksum,
        # find_duplicates_action,
        # actions.mass_update,
        # actions.calculate_checksum,
        # actions.regex_update,
        # actions.bulk_update_export,
    ]
    title = None
    title_plural = None
    list_per_page = 20

    def get_queryset(self, request: HttpRequest) -> "QuerySet[Beneficiary]":
        qs = super().get_queryset(request)
        if prg := self.get_selected_program(request):
            return qs.filter(batch__program=prg)
        else:
            return qs

    def get_common_context(self, request: HttpRequest, pk: Optional[str] = None, **kwargs: Any) -> dict[str, Any]:
        ret = super().get_common_context(request, pk, **kwargs)
        ret["datachecker"] = self.get_checker(request, ret.get("original"))
        ret["modeladmin"] = self
        ret["title_plural"] = self.title_plural
        ret.update(**kwargs)
        return ret

    @button(label=_("Validate"), enabled=lambda btn: btn.context["original"].checker)
    def validate_single(self, request: HttpRequest, pk: str) -> "HttpResponse":
        obj: "Beneficiary" = self.get_object(request, pk)
        if obj.validate_with_checker():
            self.message_user(request, _("Validation successful!"))
        else:
            self.message_user(request, _("Validation failed!"), messages.ERROR)

    @button(label=_("Validate Programme"))
    def validate_program(self, request: HttpRequest) -> "HttpResponse":
        if prg := self.get_selected_program(request):
            qs = self.get_queryset(request).filter(batch__program=prg)
            self.validate_queryset(request, qs)

    @button()
    def view_raw_data(self, request: HttpRequest, pk: str) -> "HttpResponse":
        context = self.get_common_context(request, pk, title="Raw Data")
        return render(request, f"workspace/{self.model._meta.proxy_for_model._meta.model_name}/raw_data.html", context)

    def is_valid(self, obj: "Validable") -> bool | None:
        if not obj.last_checked:
            return None
        return not bool(obj.errors)

    is_valid.boolean = True

    def get_changelist(self, request: HttpRequest, **kwargs: Any) -> type:
        from ..changelist import FlexFieldsChangeList

        if program := self.get_selected_program(request):
            return type(
                "FlexFieldsChangeList",
                (FlexFieldsChangeList,),
                {
                    "checker": self.get_checker(request),
                    "selected_program": program,
                },
            )
        return FlexFieldsChangeList

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj: Model = None):
        return False

    def _changeform_view(
        self, request: HttpRequest, object_id: str, form_url: str, extra_context: dict[str, Any]
    ) -> HttpResponse:
        context = self.get_common_context(request, object_id, **extra_context)
        # add = object_id is None
        obj = self.get_object(request, unquote(object_id))
        dc: "DataChecker" = self.get_checker(request, obj)
        try:
            form_class = dc.get_form()
        except AttributeError:
            self.message_user(
                request, _("Required datachecker not found. Please check your Program configuration."), messages.ERROR
            )
            return HttpResponseRedirect(
                reverse("workspace:workspaces_%s_view_raw_data" % self.model._meta.model_name, args=[object_id])
            )

        if request.method == "POST":
            if not self.has_change_permission(request, obj):
                raise PermissionDenied
        else:
            if not self.has_view_or_change_permission(request, obj):
                raise PermissionDenied

        if obj.flex_fields:
            initials = {k.replace("flex_fields__", ""): v for k, v in obj.flex_fields.items()}
        else:
            initials = {}
        if request.method == "POST":
            if obj:
                form: "FlexForm" = form_class(request.POST, prefix="flex_field", initial=initials)
                if form.is_valid():
                    obj.flex_fields = form.cleaned_data
                    obj.save()
                    return HttpResponseRedirect(request.META["HTTP_REFERER"])
                else:
                    self.message_user(request, "Please fixes the errors below", messages.ERROR)
        else:
            form = form_class(prefix="flex_field", initial=initials)

        context["title"] = self.title
        context["checker_form"] = form
        context["has_change_permission"] = self.has_change_permission(request)

        return TemplateResponse(request, self.change_form_template, context)

    def changelist_view(self, request: HttpRequest, extra_context: Optional[dict[str, Any]] = None) -> HttpResponse:
        context = self.get_common_context(request, title="----")
        context.update(extra_context or {})
        response = super().changelist_view(request, context)
        return response

    def change_view(
        self, request: HttpRequest, object_id: str, form_url: str = "", extra_context: Optional[dict[str, Any]] = None
    ) -> HttpResponse:
        context = self.get_common_context(request, object_id, title="")
        context.update(extra_context or {})
        response = super().change_view(request, object_id, form_url, context)
        return response

    # def log_change(self, request, obj, message):
    #     from django.contrib.admin.models import CHANGE, LogEntry
    #
    #     return LogEntry.objects.log_actions(
    #         user_id=request.user.pk,
    #         queryset=[obj],
    #         action_flag=CHANGE,
    #         change_message=message,
    #         single_object=True,
    #     )

    # def history_view(self, request, object_id, extra_context=None):
    #     self.object_history_template = self._get_object_history_template()
    #     extra_context = self.get_common_context(request, object_id)
    #     key = self.object.get_object_key("history")
    #     if not (data := cache_manager.get(key)):
    #         data = []
    #         self.object.history.get("entries", [])
    #         for d, entry in self.object.history.items():
    #             data.append({"date": d,
    #                         "diff": list(dictdiffer.diff(entry, self.object.flex_fields))})
    #             cache_manager.set(key, data)
    #     extra_context["history"] = data
    #     return super().history_view(request, object_id, extra_context)
