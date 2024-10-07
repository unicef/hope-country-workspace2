from typing import Any, Optional

from django.db import models
from django.db.models import JSONField, Q, UniqueConstraint
from django.utils.translation import gettext as _

from mptt.fields import TreeForeignKey
from mptt.managers import TreeManager
from mptt.models import MPTTModel
from mptt.querysets import TreeQuerySet


class ValidityQuerySet(TreeQuerySet):
    def active(self, *args: Any, **kwargs: Any) -> "ValidityQuerySet":
        return super().filter(valid_until__isnull=True).filter(*args, **kwargs)


class ValidityManager(TreeManager):
    _queryset_class = ValidityQuerySet


class Country(MPTTModel):
    name = models.CharField(max_length=255, db_index=True)
    short_name = models.CharField(max_length=255, db_index=True)
    iso_code2 = models.CharField(max_length=2, unique=True)
    iso_code3 = models.CharField(max_length=3, unique=True)
    iso_num = models.CharField(max_length=4, unique=True)
    parent = TreeForeignKey(
        "self",
        verbose_name=_("Parent"),
        null=True,
        blank=True,
        related_name="children",
        db_index=True,
        on_delete=models.CASCADE,
    )
    valid_from = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    valid_until = models.DateTimeField(blank=True, null=True)

    objects = ValidityManager()

    class Meta:
        verbose_name_plural = "Countries"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name

    @classmethod
    def get_choices(cls) -> "list[dict[str, Any]]":
        queryset = cls.objects.all().order_by("name")
        return [
            {
                "label": {"English(EN)": country.name},
                "value": country.iso_code3,
            }
            for country in queryset
        ]


class AreaType(MPTTModel):
    name = models.CharField(max_length=255, db_index=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    area_level = models.PositiveIntegerField(default=1)
    parent = TreeForeignKey(
        "self",
        blank=True,
        db_index=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_("Parent"),
    )
    valid_from = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    valid_until = models.DateTimeField(blank=True, null=True)
    extras = JSONField(default=dict, blank=True)

    objects = ValidityManager()

    class Meta:
        verbose_name_plural = "Area Types"
        unique_together = ("country", "area_level", "name")

    def __str__(self) -> str:
        return self.name


class Area(MPTTModel):
    name = models.CharField(max_length=255)
    parent = TreeForeignKey(
        "self",
        blank=True,
        db_index=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_("Parent"),
    )
    p_code = models.CharField(
        max_length=32, blank=True, null=True, verbose_name="P Code"
    )
    area_type = models.ForeignKey(AreaType, on_delete=models.CASCADE)

    valid_from = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    valid_until = models.DateTimeField(blank=True, null=True)
    extras = JSONField(default=dict, blank=True)

    objects = ValidityManager()

    class Meta:
        verbose_name_plural = "Areas"
        ordering = ("name",)
        constraints = [
            UniqueConstraint(
                fields=["p_code"],
                name="unique_area_p_code_not_blank",
                condition=~Q(p_code=""),
            )
        ]

    class MPTTMeta:
        order_insertion_by = ("name", "p_code")

    def __str__(self) -> str:
        return self.name

    @classmethod
    def get_admin_areas_as_choices(
        cls,
        admin_level: Optional[int] = None,
        business_area_slug: Optional[str] = None,
        *args: Any,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {}
        if admin_level:
            params["area_type__area_level"] = admin_level

        if business_area_slug:
            params["area_type__country__business_areas__slug"] = business_area_slug

        queryset = cls.objects.filter(**params).order_by("name")
        return [
            {
                "label": {"English(EN)": f"{area.name}-{area.p_code}"},
                "value": area.p_code,
            }
            for area in queryset
        ]
