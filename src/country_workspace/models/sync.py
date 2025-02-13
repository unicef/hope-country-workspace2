from typing import TYPE_CHECKING

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

from country_workspace.models.base import BaseManager, BaseModel

if TYPE_CHECKING:
    from django.db.models import Model


class SyncManager(BaseManager):
    def refresh(self) -> None:
        for record in self.all():
            record.refresh()

    def create_lookups(self) -> None:
        from hope_flex_fields.models import FieldDefinition

        ct = ContentType.objects.get_for_model(FieldDefinition)
        for m in settings.HH_LOOKUPS:
            fd = FieldDefinition.objects.get(name=f"HOPE HH {m}")
            SyncLog.objects.get_or_create(content_type=ct, object_id=fd.pk, data={"remote_url": f"lookups/{m.lower()}"})
        for m in settings.IND_LOOKUPS:
            fd = FieldDefinition.objects.get(name=f"HOPE IND {m}")
            SyncLog.objects.get_or_create(
                content_type=ct,
                object_id=fd.pk,
                data={"remote_url": "lookups/%s" % m.lower()},
            )

    def register_sync(self, model: "type[Model]") -> None:
        ct = ContentType.objects.get_for_model(model)
        SyncLog.objects.update_or_create(
            content_type=ct,
            defaults={
                "last_update_date": timezone.now(),
            },
        )


class SyncLog(BaseModel):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey("content_type", "object_id")
    last_update_date = models.DateTimeField(null=True, blank=True)
    last_id = models.CharField(max_length=255, null=True)
    data = models.JSONField(default=dict, blank=True)

    objects = SyncManager()

    def refresh(self) -> None:
        from country_workspace.contrib.hope.client import HopeClient

        fd = self.content_object
        if not fd:
            return
        if "remote_url" in self.data:
            client = HopeClient()
            record = client.get_lookup(self.data["remote_url"])
            choices = []
            for k, v in record.items():
                choices.append((k, v))
            if not fd.attrs:
                fd.attrs = {}
            fd.attrs["choices"] = choices
            fd.save()
            self.last_update_date = timezone.now()
            self.save()
