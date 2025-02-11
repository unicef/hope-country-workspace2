import functools
from typing import Any

from debug_toolbar.panels import Panel
from django.http import HttpRequest, HttpResponse
from django.utils import timezone
from django.utils.translation import gettext as _

from country_workspace.cache.signals import cache_get, cache_set, cache_store
from country_workspace.state import state


class CacheHit:
    def __init__(self, data: dict[str, str], **kwargs: Any) -> None:
        self.timestamp = timezone.now()
        self.key = data["key"]
        self.tenant = state.tenant
        self.program = state.program
        self.hit = data.get("hit", "")
        self.extra = kwargs

    def __repr__(self) -> str:
        return str(self.__dict__)


class WSCachePanel(Panel):
    title = _("Cache")
    nav_title = _("Cache")
    template = "debug_toolbar/panels/cache.html"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.gets = []
        self.sets = []
        self.stores = []

    def _log(self, action: str, **kwargs: Any) -> None:
        if action == "get":
            self.gets.append(CacheHit(kwargs))
        elif action == "set":
            self.sets.append(CacheHit(kwargs))
        elif action == "store":
            self.stores.append(CacheHit(kwargs, path=kwargs["request"].path))

    def enable_instrumentation(self) -> None:
        cache_get.connect(functools.partial(self._log, action="get"))
        cache_set.connect(functools.partial(self._log, action="set"))
        cache_store.connect(functools.partial(self._log, action="store"))

    def process_request(self, request: HttpRequest) -> HttpResponse:
        self.gets = []
        self.sets = []
        self.stores = []
        return self.get_response(request)

    @property
    def nav_subtitle(self) -> str:
        return f"~{len(self.gets)} gets / ~{len(self.sets)} sets"

    def generate_stats(self, request: HttpRequest, response: HttpResponse) -> None:
        self.record_stats(
            {
                "gets": self.gets,
                "sets": self.sets,
                "stores": self.stores,
            },
        )
