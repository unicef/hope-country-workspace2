import re
from typing import TYPE_CHECKING, Any

from django import forms
from django.contrib import messages
from django.db import transaction
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils.translation import gettext as _

from country_workspace.utils.flex_fields import get_checker_fields

from .base import BaseActionForm

if TYPE_CHECKING:
    from hope_flex_fields.models import DataChecker

    from country_workspace.types import Beneficiary
    from country_workspace.workspaces.admin.hh_ind import BeneficiaryBaseAdmin

    RegexRule = tuple[str, str]
    RegexRules = list[RegexRule]


class RegexFormField(forms.CharField):
    def clean(self, value: Any) -> Any:
        super().clean(value)
        try:
            re.compile(value)
            return value
        except Exception:
            raise forms.ValidationError("Invalid regex")


class RegexUpdateForm(BaseActionForm):
    field = forms.ChoiceField(choices=[])
    regex = RegexFormField()
    subst = forms.CharField()

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        checker: "DataChecker" = kwargs.pop("checker")
        super().__init__(*args, **kwargs)
        self.fields["field"].choices = list(get_checker_fields(checker))


def regex_update_impl(
    records: "QuerySet[Beneficiary]", config: dict[str, Any], save: bool = True
) -> list[tuple[str, str, str]]:
    if isinstance(config["regex"], str):
        config["regex"] = re.compile(config["regex"])

    field_name = config["field"]
    ret = []
    with transaction.atomic():
        for record in records:
            old_value = record.flex_fields.get(field_name, "")
            new_value = config["regex"].sub(config["subst"], old_value, 1)
            record.flex_fields[field_name] = new_value
            if save:
                record.save()
            else:
                ret.append((record.pk, old_value, new_value))
    return ret


def regex_update(
    model_admin: "BeneficiaryBaseAdmin", request: "HttpRequest", queryset: "QuerySet[Beneficiary]"
) -> HttpResponse:
    ctx = model_admin.get_common_context(request, title=_("Regex update"))
    ctx["checker"] = checker = model_admin.get_checker(request)
    ctx["queryset"] = queryset
    ctx["opts"] = model_admin.model._meta
    ctx["preserved_filters"] = model_admin.get_preserved_filters(request)
    if "_preview" in request.POST:
        form = RegexUpdateForm(request.POST, checker=checker)
        if form.is_valid():
            changes = regex_update_impl(queryset.all()[:10], form.cleaned_data, save=False)
            ctx["changes"] = changes
    elif "_apply" in request.POST:
        form = RegexUpdateForm(request.POST, checker=checker)
        if form.is_valid():
            regex_update_impl(queryset.all(), form.cleaned_data)
            model_admin.message_user(request, "Records updated successfully", messages.SUCCESS)
    else:
        form = RegexUpdateForm(
            checker=checker,
            initial={
                "action": request.POST["action"],
                "select_across": request.POST["select_across"],
                "_selected_action": request.POST.getlist("_selected_action"),
            },
        )

    ctx["form"] = form
    return render(request, "workspace/actions/regex.html", ctx)
