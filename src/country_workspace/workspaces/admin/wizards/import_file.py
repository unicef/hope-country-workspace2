from typing import Any

from django import forms  # - ImportFileForm
from django.http import HttpRequest

# - SelectMapping
# - CreateMapping
# - ScheduleJob


class WizardForm(forms.Form):

    def __init__(self, request: HttpRequest, **kwargs: Any) -> None:
        self.request = request
        super().__init__(**kwargs)


class ManagementForm(forms.Form):
    prefix = "mng"
    current_step = forms.IntegerField()


class ChannelWizard(CookieWizardView):
    form_list = (
        ("mode", ChannelType),
        ("org", SelectOrganizationForm),
        ("prj", ChannelProject),
        ("parent", ChannelSelectParent),
        ("data", ChannelData),
    )
    condition_dict = {
        # "mode": ChannelType.visible,
        "org": SelectOrganizationForm.visible,
        "prj": ChannelProject.visible,
        "parent": ChannelSelectParent.visible,
        "data": ChannelData.visible,
    }
    template_name = "admin/channel/add_view.html"
