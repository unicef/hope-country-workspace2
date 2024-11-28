import contextlib
import logging
from typing import TYPE_CHECKING, Any

from django.core.cache import cache

from redis_lock import Lock

from country_workspace.config.celery import app
from country_workspace.models import AsyncJob

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from redis_lock.django_cache import RedisCache

    cache: RedisCache


@contextlib.contextmanager
def lock_job(job: AsyncJob) -> Lock:
    lock = None
    if job.group_key:
        lock_key = f"lock:{job.group_key}"
        # Get a lock with a 60-second lifetime but keep renewing it automatically
        # to ensure the lock is held for as long as the Python process is running.
        lock = cache.lock(lock_key, 60, auto_renewal=True)
        yield lock.__enter__()
    else:
        yield
    if lock:
        lock.release()


@app.task()
def sync_job_task(pk: int, version: int) -> dict[str, Any]:
    job: AsyncJob = AsyncJob.objects.select_related("program").get(pk=pk, version=version)
    with lock_job(job):
        try:
            return job.execute()
        except Exception as e:
            logger.exception(e)
            raise


@app.task()
def removed_expired_jobs(**kwargs):
    AsyncJob.objects.filter(**kwargs).delete()
