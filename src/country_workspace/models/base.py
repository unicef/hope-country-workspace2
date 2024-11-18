from typing import TYPE_CHECKING, Any, Optional

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _

import dictdiffer
import reversion

from country_workspace.cache.manager import cache_manager
from country_workspace.state import state

if TYPE_CHECKING:
    from hope_flex_fields.models import DataChecker


class BaseQuerySet(models.QuerySet["models.Model"]):

    def get(self, *args: Any, **kwargs: Any) -> "models.Model":
        try:
            return super().get(*args, **kwargs)
        except self.model.DoesNotExist:
            raise self.model.DoesNotExist(
                "%s matching query does not exist. Using %s %s" % (self.model._meta.object_name, args, kwargs)
            )


class BaseManager(models.Manager["models.Model"]):
    _queryset_class = BaseQuerySet


class Cachable:

    def country_office(self):
        raise NotImplementedError

    def program(self):
        raise NotImplementedError

    def get_object_key(self, suffix: str = ""):
        version = str(cache_manager.get_cache_version(program=self.program))

        parts = [self.__class__.__name__, version, self.country_office.slug, str(self.program.pk), str(self.pk), suffix]
        return ":".join(parts)


class Validable(Cachable, models.Model):
    batch = models.ForeignKey("Batch", on_delete=models.CASCADE)
    last_checked = models.DateTimeField(default=None, null=True, blank=True)
    errors = models.JSONField(default=dict, blank=True, editable=False)
    flex_fields = models.JSONField(default=dict, blank=True)
    flex_files = models.BinaryField(null=True, blank=True)

    name = models.CharField(_("Name"), max_length=255)
    removed = models.BooleanField(_("Removed"), default=False)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.name or "%s %s" % (self._meta.verbose_name, self.id)

    def save(self, *args, force_insert=False, force_update=False, using=None, update_fields=None):
        with reversion.create_revision():
            super().save(
                *args, force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields
            )
            if state.request:
                reversion.set_user(state.request.user)

    def checker(self) -> "DataChecker":
        raise NotImplementedError

    def validate_with_checker(self) -> bool:
        errors = self.checker.validate([self.flex_fields])
        if errors:
            self.errors = errors[1]
        else:
            self.errors = {}
        self.last_checked = timezone.now()
        self.save(update_fields=["last_checked", "errors"])
        return not bool(errors)

    def last_changes(self) -> "Any":
        from reversion.models import Version

        last_version = Version.objects.get_for_object(self).latest("-pk")
        stored_status = last_version.field_dict["flex_fields"]
        current_status = self.flex_fields
        return list(dictdiffer.diff(stored_status, current_status))

    def diff(self, first: Optional[int] = None, second: Optional[int] = None) -> "Any":
        from reversion.models import Version

        qs = Version.objects.get_for_object(self).order_by("pk")
        versions = list(qs.values_list("pk", flat=True))
        if first is None:
            first = len(versions) - 1
        if second is None:
            second = first - 1
        v1, v2 = list(qs.filter(pk__in=[versions[first], versions[second]]))
        status1 = v1.field_dict["flex_fields"]
        status2 = v2.field_dict["flex_fields"]
        return list(dictdiffer.diff(status2, status1))


class BaseModel(models.Model):
    last_modified = models.DateTimeField(auto_now=True, editable=False)

    objects = BaseManager()

    class Meta:
        abstract = True

    def get_change_url(self, namespace: str = "workspace") -> str:
        return reverse(
            "%s:%s_%s_change" % (namespace, self._meta.app_label, self._meta.model_name),
            args=[self.pk],
        )
