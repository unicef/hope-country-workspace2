import functools
import time

from django.utils.translation import gettext as _

from debug_toolbar.panels import Panel

from country_workspace.contrib.hope.signals import hope_request_end, hope_request_start


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
        return f"{len(self.calls)} calls"

    def generate_stats(self, request, response):
        self.record_stats({"calls": self.calls})
