from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Q
from django.http import JsonResponse

from admin_extra_buttons.decorators import view
from admin_extra_buttons.mixins import ExtraButtonsMixin

from ..models import User


@admin.register(User)
class UserAdmin(ExtraButtonsMixin, BaseUserAdmin):
    def get_search_results(self, request, queryset, search_term):
        return super().get_search_results(request, queryset, search_term)

    @view()
    def autocomplete(self, request):
        filters = {}
        if term := request.GET.get("term"):
            filters["username__icontains"] = term
        qs = User.objects.filter(**filters).distinct()
        if program := request.GET.get("program"):
            qs = qs.filter(
                Q(roles__program__id=program) | Q(is_superuser=True) | Q(roles__country_office__programs__pk=program)
            )
        results = []
        for user in qs.all():
            results.append({"id": user.id, "text": user.username})
        res = {"results": results, "pagination": {"more": False}}
        return JsonResponse(res)
