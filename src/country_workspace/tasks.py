import io
import logging
from typing import Any

from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import default_storage
from django.utils.module_loading import import_string

from hope_flex_fields.models import DataChecker
from hope_smart_import.readers import open_xls

from country_workspace.config.celery import app
from country_workspace.models import AsyncJob, Program

logger = logging.getLogger(__name__)


@app.task()
def sync_job_task(pk: int, version: int) -> dict[str, Any]:
    job: AsyncJob = AsyncJob.objects.select_related("program").get(pk=pk, version=version)
    try:
        match job.type:
            case AsyncJob.JobType.FQN:
                func = import_string(job.action)
                return func(**job.config)
            case AsyncJob.JobType.BULK_UPDATE_IND:
                return bulk_update_individual(job)
            case AsyncJob.JobType.BULK_UPDATE_HH:
                return bulk_update_household(job)
            case AsyncJob.JobType.VALIDATE_PROGRAM:
                return bulk_update_household(job)
            case AsyncJob.JobType.CREATE_XLS_IMPORTER:
                return job_create_xls_importer(job)
    except Exception as e:
        logger.exception(e)
        raise


def bulk_update_individual(job: AsyncJob) -> dict[str, Any]:
    ret = {"not_found": []}
    for e in open_xls(io.BytesIO(job.file.read()), start_at=0):
        try:
            _id = e.pop("id")
            ind = job.program.individuals.get(id=_id)
            ind.flex_fields.update(**e)
            ind.save()
        except ObjectDoesNotExist:
            ret["not_found"].append(_id)
    return ret


def bulk_update_household(job: AsyncJob) -> dict[str, Any]:
    ret = {"not_found": []}
    for e in open_xls(io.BytesIO(job.file.read()), start_at=0):
        try:
            _id = e.pop("id")
            ind = job.program.households.get(id=_id)
            ind.flex_fields.update(**e)
            ind.save()
        except ObjectDoesNotExist:
            ret["not_found"].append(_id)
    return ret


def job_create_xls_importer(job: AsyncJob) -> bytes:
    from country_workspace.workspaces.admin.actions.bulk_export import create_xls_importer

    program: Program = job.program
    model = apps.get_model(job.config["model"])
    dc: DataChecker = program.get_checker_for(model)
    queryset = model.objects.filter(pk__in=job.config["records"])
    filename = "%s.xlsx" % queryset.model._meta.verbose_name_plural.lower().replace(" ", "_")
    out, __ = create_xls_importer(queryset.all(), dc, job.config)
    path = default_storage.save("%s/%s/%s" % (program.pk, job.pk, filename), out)
    return path
