from typing import Any

import django.dispatch
from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver


class CacheManager:
    def __init__(self):
        self.active = True

    def init(self):
        pass

    def invalidate(self, key):
        cache_invalidate.send(CacheManager, key=key)

    def get(self, key):
        if not self.active:
            return None
        data = cache.get(key)
        cache_get.send(CacheManager, key=key, hit=bool(data))
        return data

    def set(self, key: str, value: Any, **kwargs):
        cache_set.send(CacheManager, key=key)
        return cache.set(key, value, **kwargs)

    # def _build_key_from_request(self, request):
    #     if state.tenant and state.program:
    #         return f"{state.tenant.slug}:{state.program.pk}:
    #         {slugify(request.path)}:{slugify(str(sorted(request.GET)))}"
    #     return ""
    #
    # def store(self, request, value):
    #     key = self._build_key_from_request(request)
    #     cache_store.send(CacheManager, key=key, request=request, value=value)
    #     self.set(key, value)
    #
    # def retrieve(self, request):
    #     key = self._build_key_from_request(request)
    #     if data := cache.get(key):
    #         return pickle.loads(data)
    #     return None


cache_manager = CacheManager()

cache_get = django.dispatch.Signal()
cache_set = django.dispatch.Signal()
cache_store = django.dispatch.Signal()
cache_invalidate = django.dispatch.Signal()


@receiver(post_save)
def update_cache(sender, instance, **kwargs):
    cache_manager.invalidate(sender)
