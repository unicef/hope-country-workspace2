from typing import TYPE_CHECKING

from django import forms
from django.contrib.admin.forms import AdminAuthenticationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from django_select2 import forms as s2forms

from ..models import Program
from ..state import state
from .config import conf

if TYPE_CHECKING:
    from typing import Any

    from django.contrib.auth.base_user import AbstractBaseUser


class TenantAuthenticationForm(AdminAuthenticationForm):
    def confirm_login_allowed(self, user: "AbstractBaseUser") -> None:
        if not user.is_active:  # pragma: no cover
            raise ValidationError(self.error_messages["inactive"], code="inactive")


class SelectTenantForm(forms.Form):
    tenant = forms.ModelChoiceField(
        label=_("Office"),
        queryset=None,
        required=True,
        blank=False,
        limit_choices_to={"active": True},
    )
    next = forms.CharField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args: "Any", **kwargs: "Any") -> None:
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)
        self.fields["tenant"].queryset = conf.auth.get_allowed_tenants(self.request)


class ProgramWidget(s2forms.ModelSelect2Widget):
    model = Program
    search_fields = ["name__icontains"]

    def filter_queryset(self, request, term, queryset=None, **dependent_fields):
        qs = super().filter_queryset(request, term, queryset, **dependent_fields)
        return qs.filter(country_office=state.tenant)

    @property
    def media(self):
        original = super().media
        return original + forms.Media(
            css={
                "screen": [
                    "adminfilters/adminfilters.css",
                ]
            },
        )


class SelectProgramForm(forms.Form):
    program = forms.ModelChoiceField(
        label=_("Program"),
        queryset=None,
        required=True,
        blank=False,
        limit_choices_to={"active": True},
        widget=ProgramWidget(
            attrs={
                "data-minimum-input-length": 0,
                "data-placeholder": "Select a Program",
                "data-close-on-select": "true",
            }
        ),
    )
    next = forms.CharField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args: "Any", **kwargs: "Any") -> None:
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)
        if state.tenant:
            self.fields["program"].queryset = state.tenant.programs.filter().order_by("name").all()
