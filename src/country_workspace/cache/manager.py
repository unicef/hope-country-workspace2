from typing import TYPE_CHECKING, Any, Optional

from django.core.cache import cache
from django.utils.text import slugify

from country_workspace.state import state

from .signals import cache_get, cache_invalidate, cache_set

if TYPE_CHECKING:
    from ..models import Office, Program


class CacheManager:
    def __init__(self):
        self.active = True

    def init(self):
        from . import handlers  # noqa

    def invalidate(self, key):
        cache_invalidate.send(CacheManager, key=key)

    def get(self, key):
        if not self.active:
            return None
        data = cache.get(key)
        cache_get.send(CacheManager, key=key, hit=bool(data))
        return data

    def set(self, key: str, value: Any, timeout: int = 0, **kwargs):
        cache_set.send(self.__class__, key=key)
        cache.set(key, value, **kwargs)

    def _get_version_key(self, office: "Optional[Office]" = None, program: "Optional[Program]" = None):
        if program:
            program = program
            office = program.country_office
        elif office:
            program = None

        parts = ["key", office.slug if office else "-", str(program.pk) if program else "-"]
        return ":".join(parts)

    def reset_cache_version(self, *, office: "Optional[Office]" = None, program: "Optional[Program]" = None):
        key = self._get_version_key(office, program)
        cache.delete(key)

    def get_cache_version(self, *, office: "Optional[Office]" = None, program: "Optional[Program]" = None):
        key = self._get_version_key(office, program)
        return cache.get(key) or 1

    def incr_cache_version(self, *, office: "Optional[Office]" = None, program: "Optional[Program]" = None):

        key = self._get_version_key(office, program)
        try:
            return cache.incr(key)
        except ValueError:
            return cache.set(key, 2)

    def build_key_from_request(self, request, prefix="view", *args):
        tenant = "-"
        version = "-"
        program = "-"
        if state.tenant and state.program:
            tenant = state.tenant.slug
            program = str(state.program.pk)
            version = str(self.get_cache_version(program=state.program))
        elif state.tenant:
            tenant = state.tenant.slug
            version = str(self.get_cache_version(office=state.tenant))

        parts = [
            prefix,
            version,
            tenant,
            program,
            slugify(request.path),
            slugify(str(sorted(request.GET.items()))),
            *[str(e) for e in args],
        ]
        return ":".join(parts)

    #
    # def store(self, request, value):
    #     key = self._build_key_from_request(request)
    #     cache_store.send(CacheManager, key=key, request=request, value=value)
    #     self.set(key, value)
    #
    # def retrieve(self, request, prefix=""):
    #     key = self.build_key_from_request(request)
    #     if data := cache.get(key):
    #         return pickle.loads(data)
    #     return None


cache_manager = CacheManager()
