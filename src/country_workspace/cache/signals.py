import django.dispatch

cache_get = django.dispatch.Signal()
cache_set = django.dispatch.Signal()
cache_store = django.dispatch.Signal()
cache_invalidate = django.dispatch.Signal()
