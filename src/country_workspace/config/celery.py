import hashlib
import json
import os
from typing import Any

from django.core.cache import cache

import sentry_sdk
from celery import Celery, Task, signals

from country_workspace.config import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "country_workspace.config.settings")


class LockedTask(Task):
    lock_key = None

    def acquire_lock(self):
        """Tenta di acquisire il lock."""
        return cache.lock(self.lock_key, 60 * 60 * 24)  # 1 day TTL

    def release_lock(self):
        if self.lock_key:
            cache.delete(self.lock_key)

    def on_success(self, retval, task_id, args, kwargs):
        super().on_success(retval, task_id, args, kwargs)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        super().on_failure(exc, task_id, args, kwargs, einfo)

    def __call__(self, *args, **kwargs):
        h = hashlib.new("md5")  # nosec
        h.update(json.dumps(kwargs, sort_keys=True).encode("utf-8"))
        self.lock_key = f"lock:{self.name}:{'-'.join(map(str, args)).encode('utf-8')}:{h.hexdigest()}"
        if self.acquire_lock():
            try:
                return super().__call__(*args, **kwargs)
            finally:
                self.release_lock()
        else:
            return "Task already running"


app = Celery("cw")
app.task_cls = LockedTask
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS, related_name="tasks")


@signals.celeryd_init.connect
def init_sentry(**_kwargs: Any) -> None:
    sentry_sdk.set_tag("celery", True)
