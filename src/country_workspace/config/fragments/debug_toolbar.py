from typing import TYPE_CHECKING

from django_regex.utils import RegexList

if TYPE_CHECKING:
    from django.http import HttpRequest


def show_ddt(request: "HttpRequest") -> bool:  # pragma: no-cover
    from flags.state import flag_enabled

    if request.path in RegexList(("/api/.*", "/dal/.*", "/healthcheck/", "/autocomplete/")):
        return False
    return flag_enabled("DEVELOP_DEBUG_TOOLBAR", request=request)


DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": show_ddt,
    "JQUERY_URL": "",
}

DEBUG_TOOLBAR_PANELS = [
    "debug_toolbar.panels.request.RequestPanel",
    "debug_toolbar.panels.sql.SQLPanel",
    # "debug_toolbar.panels.staticfiles.StaticFilesPanel",
    "debug_toolbar.panels.templates.TemplatesPanel",
    "country_workspace.cache.ddt.WSCachePanel",
    "country_workspace.contrib.hope.ddt.WSHopePanel",
    # "debug_toolbar.panels.cache.CachePanel",
    "debug_toolbar.panels.signals.SignalsPanel",
    # "debug_toolbar.panels.redirects.RedirectsPanel",
    # "debug_toolbar.panels.profiling.ProfilingPanel",
    # "debug_toolbar.panels.history.HistoryPanel",
    # "debug_toolbar.panels.versions.VersionsPanel",
    # "debug_toolbar.panels.timer.TimerPanel",
    # "debug_toolbar.panels.settings.SettingsPanel",
    "debug_toolbar.panels.headers.HeadersPanel",
]
