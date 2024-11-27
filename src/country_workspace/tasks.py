import logging
from typing import Any

from country_workspace.config.celery import app
from country_workspace.models import AsyncJob

logger = logging.getLogger(__name__)


@app.task()
def sync_job_task(pk: int, version: int) -> dict[str, Any]:
    job: AsyncJob = AsyncJob.objects.select_related("program").get(pk=pk, version=version)
    try:
        return job.execute()
    except Exception as e:
        logger.exception(e)
        raise
