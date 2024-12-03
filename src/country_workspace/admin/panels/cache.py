from django import forms
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from country_workspace.cache.manager import cache_manager


class CacheManagerForm(forms.Form):
    pattern = forms.CharField()


def panel_cache(self, request):
    context = self.each_context(request)
    client = cache_manager.get_redis_client()
    limit_to = "*"

    def _get_keys():
        return list(client.scan_iter(f"*:cache:entry:{limit_to}"))

    if request.method == "POST":
        form = CacheManagerForm(request.POST)
        if form.is_valid():
            limit_to = form.cleaned_data["pattern"]
            if "_delete" in request.POST:
                to_delete = list(_get_keys())
                if to_delete:
                    client.delete(*to_delete)
    else:
        form = CacheManagerForm()

    context["title"] = "Cache Manager"
    context["form"] = form
    cache_data = _get_keys()
    context["cache_data"] = cache_data

    return render(request, "smart_admin/panels/cache.html", context)


panel_cache.verbose_name = _("Cache")  # type: ignore[attr-defined]
panel_cache.url_name = "cache"  # type: ignore[attr-defined]
