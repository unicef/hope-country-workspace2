import logging
from typing import TYPE_CHECKING

from django.apps import apps
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from strategy_field.utils import fqn

from country_workspace.state import state

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from country_workspace.types import Beneficiary
    from country_workspace.workspaces.admin.hh_ind import BeneficiaryBaseAdmin


def validate_queryset(model_name, pks) -> dict[str, int]:
    valid = invalid = num = 0
    try:
        model = apps.get_model(model_name)
        num = valid = invalid = 0
        for num, entry in enumerate(model.objects.filter(pk__in=pks), 1):
            if entry.validate_with_checker():
                valid += 1
            else:
                invalid += 1
    except Exception as e:
        logger.exception(e)

    return {"valid": valid, "invalid": invalid, "total": num}


@admin.action(description="Validate selected records")
def validate_queryset_async(
    model_admin: "BeneficiaryBaseAdmin", request: HttpRequest, queryset: "QuerySet[Beneficiary]"
) -> None:
    from country_workspace.models import AsyncJob

    opts = queryset.model._meta
    job = AsyncJob.objects.create(
        description="Validate Queryset records for updates",
        type=AsyncJob.JobType.FQN,
        owner=state.request.user,
        action=fqn(validate_queryset),
        program=state.program,
        config={"pks": list(queryset.values_list("pk", flat=True)), "model_name": opts.label},
    )
    job.queue()
    return job
