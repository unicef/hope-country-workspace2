from redis_lock import Lock

from country_workspace.models import AsyncJob
from country_workspace.tasks import lock_job


def test_lock():
    with lock_job(AsyncJob(group_key="abc")) as lock:
        assert isinstance(lock, Lock)
        assert lock.locked()
    assert not lock.locked()
    with lock_job(AsyncJob()) as lock:
        assert lock is None
