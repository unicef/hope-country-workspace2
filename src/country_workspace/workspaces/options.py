from typing import TYPE_CHECKING, Any
from urllib.parse import urlencode

from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.admin import ShowFacets
from django.db.models import Model
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse

from admin_extra_buttons.mixins import ExtraButtonsMixin
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.mixin import AdminFiltersMixin
from smart_admin.mixins import SmartFilterMixin

from country_workspace.workspaces.templatetags.workspace_urls import add_preserved_filters

if TYPE_CHECKING:
    from .changelist import WorkspaceChangeList


class WorkspaceAutoCompleteFilter(AutoCompleteFilter):
    def get_url(self) -> str:
        return reverse("%s:autocomplete" % self.admin_site.namespace)


class WorkspaceModelAdmin(ExtraButtonsMixin, AdminFiltersMixin, SmartFilterMixin, admin.ModelAdmin):
    # change_list_template = "workspace/change_list.html"
    # change_form_template = "workspace/change_form.html"
    object_history_template = "workspace/object_history.html"
    delete_selected_confirmation_template = "workspace/delete_selected_confirmation.html"
    delete_confirmation_template = "workspace/delete_confirmation.html"
    list_select_related = True
    preserve_filters = True
    default_url_filters = {}
    actions_selection_counter = True
    show_facets = ShowFacets.NEVER
    show_full_result_count = False

    def _get_change_form_template(self):
        return [
            # "workspace/%s/%s/change_form.html" % (self.opts.app_label, self.opts.model_name),
            "workspace/%s/change_form.html" % self.opts.proxy_for_model._meta.model_name,
            # "workspace/%s/change_form.html" % self.opts.app_label,
            "workspace/change_form.html",
        ]

    def _get_changelist_template(self):
        return [
            # "workspace/%s/%s/change_form.html" % (self.opts.app_label, self.opts.model_name),
            "workspace/%s/change_list.html" % self.opts.proxy_for_model._meta.model_name,
            # "workspace/%s/change_form.html" % self.opts.app_label,
            "workspace/change_list.html",
        ]

    def _get_object_history_template(self):
        return [
            "workspace/%s/object_history.html" % self.opts.proxy_for_model._meta.model_name,
            "workspace/object_history.html",
        ]

    def get_common_context(self, request, pk=None, **kwargs):
        kwargs["modeladmin"] = self
        return super().get_common_context(request, pk, **kwargs)

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    @property
    def media(self):
        extra = "" if settings.DEBUG else ".min"
        base = super().media
        return base + forms.Media(
            js=[
                "workspace/js/cl%s.js" % extra,
            ],
            css={},
        )

    def get_preserved_filters(self, request: HttpRequest) -> dict[str, str]:
        """
        Return the preserved filters querystring.
        """
        match = request.resolver_match
        if self.preserve_filters and match:
            current_url = "%s:%s" % (match.app_name, match.url_name)
            changelist_url = "%s:%s_%s_changelist" % (
                self.admin_site.namespace,
                self.opts.app_label,
                self.opts.model_name,
            )
            if current_url == changelist_url:
                preserved_filters = request.GET.urlencode()
            else:
                preserved_filters = request.GET.get("_changelist_filters")

            if preserved_filters:
                return urlencode({"_changelist_filters": preserved_filters})
        return ""

    def add_preserved_filters(self, request: HttpRequest, base_url: str) -> str:
        preserved_filters = self.get_preserved_filters(request)
        preserved_qsl = self._get_preserved_qsl(request, preserved_filters)
        return add_preserved_filters(
            {
                "preserved_filters": preserved_filters,
                "preserved_qsl": preserved_qsl,
                "opts": self.model._meta,
            },
            base_url,
        )

    def get_default_url_filters(self, request: "HttpRequest"):
        return self.default_url_filters

    def get_changelist_index_url(self, request: "HttpRequest"):
        bsse = self.get_changelist_url()
        return f"{bsse}?{urlencode(self.get_default_url_filters(request))}"

    def get_changelist_url(self):
        opts = self.model._meta
        return reverse(
            "%s:%s_%s_changelist" % (self.admin_site.namespace, opts.app_label, opts.model_name),
            current_app=self.admin_site.name,
        )

    def get_change_url(self, request: "HttpRequest", obj: Model) -> str:
        opts = self.model._meta
        obj_url = reverse(
            "%s:%s_%s_change" % (self.admin_site.namespace, opts.app_label, opts.model_name),
            args=[obj.pk],
            current_app=self.admin_site.name,
        )
        return obj_url

    def get_changelist(self, request: "HttpRequest", **kwargs) -> "type[WorkspaceChangeList]":
        from .changelist import WorkspaceChangeList

        return WorkspaceChangeList

    # @csrf_protect_m
    def changeform_view(self, request: "HttpRequest", object_id=None, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context["show_save_and_add_another"] = False
        extra_context["show_save_and_continue"] = True
        extra_context["show_save"] = False
        extra_context["preserved_filters"] = self.get_preserved_filters(request)
        return super().changeform_view(request, object_id, form_url, extra_context=extra_context)

    def changelist_view(self, request, extra_context=None):
        self.change_list_template = self._get_changelist_template()
        extra_context = extra_context or {}
        extra_context["preserved_filters"] = self.get_preserved_filters(request)
        return super().changelist_view(request, extra_context=extra_context)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        self.change_form_template = self._get_change_form_template()
        return super().change_view(request, object_id, form_url=form_url, extra_context=extra_context)

    def _response_post_save(self, request: "HttpRequest", obj):
        return HttpResponseRedirect(self.add_preserved_filters(request, self.get_changelist_url()))

    def response_add(self, request: "HttpRequest", obj, post_url_continue=None):
        return HttpResponseRedirect(self.get_change_url(request, obj))

    def response_delete(self, request: "HttpRequest", obj_display, obj_id: Any) -> HttpResponseRedirect:
        return HttpResponseRedirect(self.get_changelist_url())
