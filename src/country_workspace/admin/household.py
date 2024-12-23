from typing import TYPE_CHECKING

from django.contrib import admin, messages
from django.urls import reverse
from django.utils.translation import gettext as _

from admin_extra_buttons.buttons import LinkButton
from admin_extra_buttons.decorators import button, link
from adminfilters.autocomplete import LinkedAutoCompleteFilter

from ..models import Household
from .base import BaseModelAdmin
from .filters import IsValidFilter

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse


@admin.register(Household)
class HouseholdAdmin(BaseModelAdmin):
    list_display = ("name", "country_office", "program", "batch")
    list_filter = (
        ("batch__country_office", LinkedAutoCompleteFilter.factory(parent=None)),
        ("batch__program", LinkedAutoCompleteFilter.factory(parent="batch__country_office")),
        ("batch", LinkedAutoCompleteFilter.factory(parent="batch__program")),
        IsValidFilter,
    )
    readonly_fields = ("errors",)
    search_fields = ("name",)
    autocomplete_fields = ("batch",)

    @link(change_list=False)
    def members(self, button: LinkButton) -> None:
        base = reverse("admin:country_workspace_individual_changelist")
        obj = button.context["original"]
        button.href = f"{base}?household__exact={obj.pk}"

    @link(change_list=True, change_form=False)
    def view_in_workspace(self, btn: "LinkButton") -> None:
        if "request" in btn.context:
            req = btn.context["request"]
            base = reverse("workspace:workspaces_countryhousehold_changelist")
            btn.href = f"{base}?%s" % req.META["QUERY_STRING"]

    @button(label=_("Validate"), enabled=lambda btn: btn.context["original"].checker)
    def validate_single(self, request: "HttpRequest", pk: str) -> "HttpResponse":
        obj: "Household" = self.get_object(request, pk)
        if obj.validate_with_checker():
            self.message_user(request, _("Validation successful!"), messages.SUCCESS)
        else:
            self.message_user(request, _("Validation failed!"), messages.ERROR)
