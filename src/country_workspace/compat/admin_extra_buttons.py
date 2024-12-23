from django.contrib import messages
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse


def confirm_action(  # noqa: PLR0913
    modeladmin,
    request,
    action,
    message,
    success_message="",
    description="",
    pk=None,
    extra_context=None,
    title=None,
    template="admin_extra_buttons/confirm.html",
    error_message=None,
    raise_exception=False,
):
    opts = modeladmin.model._meta
    if extra_context:
        title = extra_context.pop("title", title)
    context = modeladmin.get_common_context(
        request, message=message, description=description, title=title, pk=pk, **(extra_context or {})
    )
    if request.method == "POST":
        ret = None
        try:
            ret = action(request)
            if success_message:
                modeladmin.message_user(request, success_message, messages.SUCCESS)
        except Exception as e:  # pragma: no cover
            if raise_exception:
                raise
            if error_message:
                modeladmin.message_user(request, error_message or str(e), messages.ERROR)
        if ret:
            return ret
        return HttpResponseRedirect(reverse(admin_urlname(opts, "changelist")))

    return TemplateResponse(request, template, context)
