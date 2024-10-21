from typing import Any, Optional

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.admin import register
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _

from admin_extra_buttons.api import button, link
from admin_extra_buttons.buttons import LinkButton
from hope_flex_fields.models import DataChecker
from strategy_field.utils import fqn

from country_workspace.state import state

from ...datasources.rdi import import_from_rdi_job
from ...models import AsyncJob, Batch
from ...contrib.aurora.forms import ImportAuroraForm
from ...utils.flex_fields import get_checker_fields
from ..models import CountryProgram
from ..options import WorkspaceModelAdmin
from ..sites import workspace
from .cleaners.bulk_update import bulk_update_household, bulk_update_individual
from .forms import ImportFileForm


class SelectColumnsForm(forms.Form):
    columns = forms.MultipleChoiceField(choices=(), widget=forms.CheckboxSelectMultiple)
    model_core_fields = [("name", "name"), ("id", "id")]

    def __init__(self, *args: Any, **kwargs: Any):
        self.checker: "DataChecker" = kwargs.pop("checker")
        super().__init__(*args, **kwargs)
        columns: list[tuple[str, str]] = []

        for name, label in get_checker_fields(self.checker):
            columns.append((f"flex_fields__{name}", label))

        self.fields["columns"].choices = self.model_core_fields + sorted(columns)


class SelectIndividualColumnsForm(SelectColumnsForm):
    model_core_fields = [("name", "name"), ("id", "id"), ("household", "household")]


class ProgramForm(forms.ModelForm):
    class Meta:
        model = CountryProgram
        exclude = ("country_office",)


class BulkUpdateImportForm(forms.Form):
    description = forms.CharField(widget=forms.Textarea)
    target = forms.ChoiceField(choices=(("hh", "Household"), ("ind", "Individual")))
    file = forms.FileField()


@register(CountryProgram, site=workspace)
class CountryProgramAdmin(WorkspaceModelAdmin):
    list_display = (
        "name",
        "sector",
        "status",
        "active",
    )
    search_fields = ("name",)
    list_filter = ("status", "active", "sector")
    exclude = ("country_office",)
    default_url_filters = {"status__exact": CountryProgram.ACTIVE}
    readonly_fields = (
        "individual_columns",
        "household_columns",
        "active",
        "code",
        "status",
        "sector",
        "name",
    )
    form = ProgramForm
    ordering = ("name",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    ("name", "code"),
                    ("status", "sector", "active"),
                )
            },
        ),
        (_("Validators"), {"fields": ("beneficiary_validator", ("household_checker", "individual_checker"))}),
        (
            _("Columns"),
            {
                "fields": (
                    "household_columns",
                    "individual_columns",
                ),
            },
        ),
        # (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    @property
    def media(self):
        extra = "" if settings.DEBUG else ".min"
        base = super().media
        return base + forms.Media(
            js=[
                "workspace/js/program%s.js" % extra,
            ],
            css={},
        )

    # change_form_template = "workspace/program/change_form.html"
    def get_queryset(self, request: HttpResponse) -> QuerySet[CountryProgram]:
        return CountryProgram.objects.filter(country_office=state.tenant)

    def has_add_permission(self, request: HttpResponse) -> bool:
        return False

    def has_delete_permission(self, request: HttpResponse, obj: Optional[CountryProgram] = None) -> bool:
        return False

    def changelist_view(self, request, extra_context=None):
        url = reverse("workspace:workspaces_countryprogram_change", args=[state.program.pk])
        return HttpResponseRedirect(url)

    @link(change_list=False)
    def population(self, btn: LinkButton) -> None:
        btn.href = reverse("workspace:workspaces_countryhousehold_changelist")

    def _configure_columns(
        self,
        request: HttpResponse,
        form_class: "type[SelectColumnsForm|SelectIndividualColumnsForm]",
        context: dict[str, Any],
    ) -> "HttpResponse":

        program: "CountryProgram" = context["original"]
        checker: DataChecker = context["checker"]

        # initials = [s.replace("flex_fields__", "") for s in getattr(program, context["storage_field"]).split("\n")]
        initials = [s for s in getattr(program, context["storage_field"]).split("\n")]

        if request.method == "POST":
            form = form_class(
                request.POST,
                checker=checker,
                initial={"columns": initials},
            )
            if form.is_valid():
                columns = []
                for s in form.cleaned_data["columns"]:
                    columns.append(s)
                setattr(program, context["storage_field"], "\n".join(columns))
                program.save()
                return HttpResponseRedirect(reverse("workspace:workspaces_countryprogram_change", args=[program.pk]))
        else:
            form = form_class(checker=checker, initial={"columns": initials})
        context["form"] = form

        return render(request, "workspace/program/configure_columns.html", context)

    @button()
    def household_columns(self, request: HttpResponse, pk: str) -> "HttpResponse | HttpResponseRedirect":
        context = self.get_common_context(request, pk, title="Configure default Household columns")
        program: "CountryProgram" = context["original"]
        context["checker"]: "DataChecker" = program.household_checker
        context["storage_field"] = "household_columns"
        return self._configure_columns(request, SelectColumnsForm, context)

    @button()
    def individual_columns(self, request: HttpResponse, pk: str) -> "HttpResponse | HttpResponseRedirect":
        context = self.get_common_context(request, pk, title="Configure default Individual columns")
        program: "CountryProgram" = context["original"]
        context["checker"]: "DataChecker" = program.individual_checker
        context["storage_field"] = "individual_columns"
        return self._configure_columns(request, SelectIndividualColumnsForm, context)

    @button(label=_("Import File"))
    def import_rdi(self, request: HttpRequest, pk: str) -> "HttpResponse":
        context = self.get_common_context(request, pk, title="Import RDI file")
        program: "CountryProgram" = context["original"]
        context["selected_program"] = context["original"]
        if request.method == "POST":
            form = ImportFileForm(request.POST, request.FILES)
            if form.is_valid():
                batch, __ = Batch.objects.get_or_create(
                    name=form.cleaned_data["batch_name"] or ("Batch %s" % timezone.now()),
                    program=program,
                    country_office=program.country_office,
                    imported_by=state.request.user,
                )
                job: AsyncJob = AsyncJob.objects.create(
                    type=AsyncJob.JobType.TASK,
                    action=fqn(import_from_rdi_job),
                    file=request.FILES["file"],
                    program=program,
                    owner=request.user,
                    config={
                        "batch": batch.pk,
                        "household_pk_col": form.cleaned_data["pk_column_name"],
                        "master_column_label": form.cleaned_data["master_column_label"],
                        "detail_column_label": form.cleaned_data["detail_column_label"],
                    },
                )
                job.queue()
                self.message_user(request, _("Import scheduled"), messages.SUCCESS)
                context["form"] = form

        else:
            form = ImportFileForm()
        context["form"] = form
        return render(request, "workspace/program/import_rdi.html", context)

    @button(label=_("Import File Updates"))
    def import_file_updates(self, request: HttpRequest, pk: str) -> "HttpResponse":
        context = self.get_common_context(request, pk, title="Import updates from file")
        program: "CountryProgram" = context["original"]
        context["selected_program"] = context["original"]
        updated = 0
        function_map = {"hh": fqn(bulk_update_household), "ind": fqn(bulk_update_individual)}
        if request.method == "POST":
            form = BulkUpdateImportForm(request.POST, request.FILES)
            if form.is_valid():
                job = AsyncJob.objects.create(
                    description=form.cleaned_data["description"],
                    program=program,
                    owner=request.user,
                    type=AsyncJob.JobType.TASK,
                    action=function_map[form.cleaned_data["target"]],
                    batch=None,
                    file=request.FILES["file"],
                    config={},
                )
                job.queue()
                self.message_user(request, _("Import scheduled").format(updated))
                return HttpResponseRedirect(self.get_changelist_url())

        else:
            form = BulkUpdateImportForm()
        context["form"] = form
        return render(request, "workspace/actions/bulk_update_import.html", context)

    @button(label=_("Import from Aurora"))
    def import_aurora(self, request: HttpRequest, pk: str) -> "HttpResponse":
        context = self.get_common_context(request, pk, title="Import from Aurora")
        program: CountryProgram = context["original"]
        context["selected_program"] = context["original"]
        if request.method == "POST":
            form = ImportAuroraForm(request.POST)
            if form.is_valid():
                j: AsyncJob = AsyncJob.objects.create(
                    program=program,
                    type=AsyncJob.JobType.AURORA_SYNC,
                    batch=None,
                    file=None,
                    config={**form.cleaned_data, "imported_by_id": request.user.id},
                )
                j.queue()
                self.message_user(
                    request,
                    _("The import task from Aurora has been successfully queued. Asynchronous task ID: {0}.").format(
                        j.curr_async_result_id
                    ),
                    level="success",
                )
                return HttpResponseRedirect(self.get_changelist_url())
        else:
            form = ImportAuroraForm()
        context["form"] = form
        return render(request, "workspace/program/import_aurora.html", context)
