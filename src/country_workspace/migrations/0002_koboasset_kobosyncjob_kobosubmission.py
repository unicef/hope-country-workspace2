# Generated by Django 5.1.2 on 2024-11-21 09:02

import concurrency.fields
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("country_workspace", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="KoboAsset",
            fields=[
                ("uid", models.CharField(max_length=32, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name="KoboSyncJob",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("version", concurrency.fields.AutoIncVersionField(default=0, help_text="record revision number")),
                (
                    "curr_async_result_id",
                    models.CharField(
                        blank=True,
                        editable=False,
                        help_text="Current (active) AsyncResult is",
                        max_length=36,
                        null=True,
                    ),
                ),
                (
                    "last_async_result_id",
                    models.CharField(
                        blank=True, editable=False, help_text="Latest executed AsyncResult is", max_length=36, null=True
                    ),
                ),
                ("datetime_created", models.DateTimeField(auto_now_add=True, help_text="Creation date and time")),
                (
                    "datetime_queued",
                    models.DateTimeField(
                        blank=True, help_text="Queueing date and time", null=True, verbose_name="Queued At"
                    ),
                ),
                (
                    "repeatable",
                    models.BooleanField(
                        blank=True, default=False, help_text="Indicate if the job can be repeated as-is"
                    ),
                ),
                ("celery_history", models.JSONField(blank=True, default=dict, editable=False)),
                ("local_status", models.CharField(blank=True, default="", editable=False, max_length=100, null=True)),
                (
                    "group_key",
                    models.CharField(
                        blank=True,
                        editable=False,
                        help_text="Tasks with the same group key will not run in parallel",
                        max_length=255,
                        null=True,
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(app_label)s_%(class)s_jobs",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
                "default_permissions": ("add", "change", "delete", "view", "queue", "terminate", "inspect", "revoke"),
            },
        ),
        migrations.CreateModel(
            name="KoboSubmission",
            fields=[
                ("uuid", models.UUIDField(primary_key=True, serialize=False)),
                ("data", models.JSONField()),
                (
                    "asset",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="country_workspace.koboasset"),
                ),
            ],
        ),
    ]
