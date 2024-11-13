import functools
import time

from django.utils import timezone
from django.utils.translation import gettext as _

from debug_toolbar.panels import Panel

from country_workspace.cache import cache_get, cache_set, cache_store
from country_workspace.contrib.hope.signals import hope_request_end, hope_request_start
from country_workspace.state import state


class CacheHit:
    def __init__(self, data, **kwargs):
        self.timestamp = timezone.now()
        self.key = data["key"]
        self.tenant = state.tenant.name
        self.program = state.program.name
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
        return "{} gets / {} sets".format(len(self.gets), len(self.sets))

    def generate_stats(self, request, response):
        self.record_stats(
            {
                "gets": self.gets,
                "sets": self.sets,
                "stores": self.stores,
            }
        )


class ApiCall:
    def __init__(self, panel: "WSHopePanel", data):
        self.panel = panel
        self.url = data["url"]
        self.params = data["params"]
        self.signature = data["signature"]

    def timing(self):
        return self.panel.timing.get(self.signature)


class WSHopePanel(Panel):
    title = _("Hope")
    nav_title = _("Hope")
    template = "debug_toolbar/panels/hope.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.calls = []
        self.timing = {}

    def enable_instrumentation(self):
        hope_request_start.connect(functools.partial(self.log, action="start"))
        hope_request_end.connect(functools.partial(self.log, action="end"))

    def log(self, **kwargs):

        if kwargs["action"] == "start":
            self.timing[kwargs["signature"]] = time.perf_counter()
            self.calls.append(ApiCall(self, kwargs))
        elif kwargs["action"] == "end":
            s = self.timing[kwargs["signature"]]
            e = time.perf_counter()
            self.timing[kwargs["signature"]] = f"{1000 * (e - s):.3f}ms"

    def process_request(self, request):
        self.calls = []
        self.timing = {}
        return self.get_response(request)

    @property
    def nav_subtitle(self):
        return "{} calls".format(len(self.calls))

    def generate_stats(self, request, response):
        self.record_stats({"calls": self.calls})
