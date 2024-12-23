import functools

from django.utils import timezone
from django.utils.translation import gettext as _

from debug_toolbar.panels import Panel

from country_workspace.cache.signals import cache_get, cache_set, cache_store
from country_workspace.state import state


class CacheHit:
    def __init__(self, data, **kwargs):
        self.timestamp = timezone.now()
        self.key = data["key"]
        self.tenant = state.tenant
        self.program = state.program
        self.hit = data.get("hit", "")
        self.extra = kwargs

    def __repr__(self):
        return str(self.__dict__)


class WSCachePanel(Panel):
    title = _("Cache")
    nav_title = _("Cache")
    template = "debug_toolbar/panels/cache.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gets = []
        self.sets = []
        self.stores = []

    def _log(self, action, **kwargs):
        if action == "get":
            self.gets.append(CacheHit(kwargs))
        elif action == "set":
            self.sets.append(CacheHit(kwargs))
        elif action == "store":
            self.stores.append(CacheHit(kwargs, path=kwargs["request"].path))

    def enable_instrumentation(self):
        cache_get.connect(functools.partial(self._log, action="get"))
        cache_set.connect(functools.partial(self._log, action="set"))
        cache_store.connect(functools.partial(self._log, action="store"))

    def process_request(self, request):
        self.gets = []
        self.sets = []
        self.stores = []
        return self.get_response(request)

    @property
    def nav_subtitle(self):
        return f"~{len(self.gets)} gets / ~{len(self.sets)} sets"

    def generate_stats(self, request, response):
        self.record_stats(
            {
                "gets": self.gets,
                "sets": self.sets,
                "stores": self.stores,
            }
        )
