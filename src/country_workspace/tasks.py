import contextlib
import logging
from typing import TYPE_CHECKING, Any

from constance import config
from django.core.cache import cache
import sentry_sdk
from redis_lock import Lock

from country_workspace.config.celery import app
from country_workspace.contrib.kobo.client import Client as KoboClient
from country_workspace.models import AsyncJob, KoboAsset, KoboSubmission
from country_workspace.models.jobs import KoboSyncJob
from country_workspace.models.kobo import KoboQuestion

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
    try:
        job: AsyncJob = AsyncJob.objects.select_related("program", "program__country_office", "owner").get(
            pk=pk,
            version=version,
        )
    except AsyncJob.DoesNotExist as e:
        sentry_sdk.capture_exception(e)
        raise e

    with lock_job(job):
        try:
            scope = sentry_sdk.get_current_scope()
            sentry_sdk.set_tag("business_area", job.program.country_office.slug)
            sentry_sdk.set_tag("project", job.program.name)
            sentry_sdk.set_user = {"id": job.owner.pk, "email": job.owner.email}
            return job.execute()
        except Exception:
            # error is logged in job.execute
            raise
        finally:
            scope.clear()


@app.task()
def removed_expired_jobs(**kwargs: Any) -> None:
    AsyncJob.objects.filter(**kwargs).delete()

@app.task
def sync_kobo_assets_task(job_id: int, version: int) -> None:
    _ = KoboSyncJob.objects.get(pk=job_id, version=version)
    client = KoboClient(base_url=config.KOBO_BASE_URL, token=config.KOBO_TOKEN)
    for asset_data in client.assets:
        asset_model, _ = KoboAsset.objects.update_or_create(uid=asset_data.uid, defaults={"name": asset_data.name})

        for question_data in asset_data.questions:
            KoboQuestion.objects.update_or_create(asset=asset_model, key=question_data.key, labels=question_data.labels)

        for submission_data in asset_data.submissions:
            KoboSubmission.objects.update_or_create(uuid=submission_data.uuid, asset=asset_model, data=submission_data.data)
