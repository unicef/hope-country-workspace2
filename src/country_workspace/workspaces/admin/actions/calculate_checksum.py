from typing import TYPE_CHECKING

from admin_extra_buttons.utils import HttpResponseRedirectToReferrer

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.http import HttpRequest, HttpResponse

    from country_workspace.models.base import Validable
    from country_workspace.workspaces.admin.hh_ind import BeneficiaryBaseAdmin


def calculate_checksum(
    model_admin: "BeneficiaryBaseAdmin", request: "HttpRequest", queryset: "QuerySet[Validable]"
) -> "HttpResponse":
    for record in queryset.all():
        record.save()
    return HttpResponseRedirectToReferrer(request=request)
