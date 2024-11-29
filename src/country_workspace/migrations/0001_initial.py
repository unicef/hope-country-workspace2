# Generated by Django 5.1.3 on 2024-11-29 04:20

import concurrency.fields
import country_workspace.models.base
import django.contrib.auth.models
import django.contrib.auth.validators
import django.contrib.postgres.fields
import django.db.models.deletion
import django.utils.timezone
import mptt.fields
import strategy_field.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("contenttypes", "0002_remove_content_type_name"),
        ("hope_flex_fields", "0013_fielddefinition_validated_alter_datachecker_id_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Country",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("last_modified", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(db_index=True, max_length=255)),
                ("iso_code2", models.CharField(max_length=2, unique=True)),
            ],
            options={
                "verbose_name_plural": "Countries",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="Office",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("last_modified", models.DateTimeField(auto_now=True)),
                ("hope_id", models.CharField(blank=True, max_length=100, null=True, unique=True)),
                ("long_name", models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ("name", models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ("code", models.CharField(blank=True, db_index=True, max_length=100, null=True, unique=True)),
                ("slug", models.SlugField(blank=True, max_length=100, null=True, unique=True)),
                ("active", models.BooleanField(default=False)),
                ("extra_fields", models.JSONField(blank=True, default=dict)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="User",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        error_messages={"unique": "A user with that username already exists."},
                        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        max_length=150,
                        unique=True,
                        validators=[django.contrib.auth.validators.UnicodeUsernameValidator()],
                        verbose_name="username",
                    ),
                ),
                ("first_name", models.CharField(blank=True, max_length=150, verbose_name="first name")),
                ("last_name", models.CharField(blank=True, max_length=150, verbose_name="last name")),
                ("email", models.EmailField(blank=True, max_length=254, verbose_name="email address")),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                ("date_joined", models.DateTimeField(default=django.utils.timezone.now, verbose_name="date joined")),
                ("azure_id", models.UUIDField(blank=True, null=True, unique=True)),
                ("job_title", models.CharField(blank=True, max_length=100, null=True)),
                ("display_name", models.CharField(blank=True, max_length=100, null=True)),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="AreaType",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("hope_id", models.CharField(editable=False, max_length=200, unique=True)),
                ("name", models.CharField(db_index=True, max_length=255)),
                ("area_level", models.PositiveIntegerField(default=1)),
                ("valid_from", models.DateTimeField(auto_now_add=True, null=True)),
                ("valid_until", models.DateTimeField(blank=True, null=True)),
                ("extras", models.JSONField(blank=True, default=dict)),
                ("lft", models.PositiveIntegerField(editable=False)),
                ("rght", models.PositiveIntegerField(editable=False)),
                ("tree_id", models.PositiveIntegerField(db_index=True, editable=False)),
                ("level", models.PositiveIntegerField(editable=False)),
                (
                    "parent",
                    mptt.fields.TreeForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="country_workspace.areatype",
                        verbose_name="Parent",
                    ),
                ),
                (
                    "country",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="country_workspace.country"),
                ),
            ],
            options={
                "verbose_name_plural": "Area Types",
                "unique_together": {("country", "area_level", "name")},
            },
        ),
        migrations.CreateModel(
            name="Batch",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("last_modified", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(blank=True, max_length=255, null=True)),
                ("import_date", models.DateTimeField(auto_now=True)),
                (
                    "imported_by",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
                ),
                (
                    "country_office",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)ss",
                        to="country_workspace.office",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Household",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("last_checked", models.DateTimeField(blank=True, default=None, null=True)),
                ("errors", models.JSONField(blank=True, default=dict, editable=False)),
                ("flex_fields", models.JSONField(blank=True, default=dict)),
                ("flex_files", models.BinaryField(blank=True, null=True)),
                ("name", models.CharField(max_length=255, verbose_name="Name")),
                ("removed", models.BooleanField(default=False, verbose_name="Removed")),
                (
                    "checksum",
                    models.CharField(blank=True, db_index=True, max_length=300, null=True, verbose_name="checksum"),
                ),
                ("last_modified", models.DateTimeField(auto_now=True)),
                ("system_fields", models.JSONField(blank=True, default=dict)),
                ("batch", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="country_workspace.batch")),
            ],
            options={
                "verbose_name": "Household",
            },
            bases=(country_workspace.models.base.Cachable, models.Model),
        ),
        migrations.CreateModel(
            name="Individual",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("last_checked", models.DateTimeField(blank=True, default=None, null=True)),
                ("errors", models.JSONField(blank=True, default=dict, editable=False)),
                ("flex_fields", models.JSONField(blank=True, default=dict)),
                ("flex_files", models.BinaryField(blank=True, null=True)),
                ("name", models.CharField(max_length=255, verbose_name="Name")),
                ("removed", models.BooleanField(default=False, verbose_name="Removed")),
                (
                    "checksum",
                    models.CharField(blank=True, db_index=True, max_length=300, null=True, verbose_name="checksum"),
                ),
                ("last_modified", models.DateTimeField(auto_now=True)),
                ("system_fields", models.JSONField(blank=True, default=dict)),
                ("batch", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="country_workspace.batch")),
                (
                    "household",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="members",
                        to="country_workspace.household",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=(country_workspace.models.base.Cachable, models.Model),
        ),
        migrations.CreateModel(
            name="Program",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("last_modified", models.DateTimeField(auto_now=True)),
                ("hope_id", models.CharField(editable=False, max_length=200, unique=True)),
                ("name", models.CharField(max_length=255)),
                ("code", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[("ACTIVE", "Active"), ("DRAFT", "Draft"), ("FINISHED", "Finished")],
                        db_index=True,
                        max_length=10,
                    ),
                ),
                (
                    "sector",
                    models.CharField(
                        choices=[
                            ("CHILD_PROTECTION", "Child Protection"),
                            ("EDUCATION", "Education"),
                            ("HEALTH", "Health"),
                            ("MULTI_PURPOSE", "Multi Purpose"),
                            ("NUTRITION", "Nutrition"),
                            ("SOCIAL_POLICY", "Social Policy"),
                            ("WASH", "WASH"),
                        ],
                        db_index=True,
                        max_length=50,
                    ),
                ),
                ("active", models.BooleanField(default=False)),
                (
                    "beneficiary_validator",
                    strategy_field.fields.StrategyField(
                        blank=True, default="country_workspace.validators.registry.NoopValidator", null=True
                    ),
                ),
                ("household_search", models.TextField(default="name", help_text="Fields to use for searches")),
                ("individual_search", models.TextField(default="name", help_text="Fields to use for searches")),
                (
                    "household_columns",
                    models.TextField(default="name\nid", help_text="Columns to display ib the Admin table"),
                ),
                (
                    "individual_columns",
                    models.TextField(default="name\nid", help_text="Columns to display ib the Admin table"),
                ),
                ("extra_fields", models.JSONField(blank=True, default=dict)),
                (
                    "country_office",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="programs",
                        to="country_workspace.office",
                    ),
                ),
                (
                    "household_checker",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="hope_flex_fields.datachecker",
                    ),
                ),
                (
                    "individual_checker",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="hope_flex_fields.datachecker",
                    ),
                ),
            ],
            options={
                "verbose_name": "Programme",
                "verbose_name_plural": "Programmes",
            },
        ),
        migrations.AddField(
            model_name="batch",
            name="program",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="%(class)ss", to="country_workspace.program"
            ),
        ),
        migrations.CreateModel(
            name="AsyncJob",
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
                    "type",
                    models.CharField(
                        choices=[("FQN", "Operation"), ("ACTION", "Action"), ("TASK", "Task")], max_length=50
                    ),
                ),
                ("file", models.FileField(blank=True, null=True, upload_to="updates")),
                ("config", models.JSONField(blank=True, default=dict)),
                ("action", models.CharField(blank=True, max_length=500, null=True)),
                ("description", models.CharField(blank=True, max_length=255, null=True)),
                ("sentry_id", models.CharField(blank=True, max_length=255, null=True)),
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
                (
                    "batch",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="jobs",
                        to="country_workspace.batch",
                    ),
                ),
                (
                    "program",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="jobs", to="country_workspace.program"
                    ),
                ),
            ],
            options={
                "abstract": False,
                "default_permissions": ("add", "change", "delete", "view", "queue", "terminate", "inspect", "revoke"),
            },
        ),
        migrations.CreateModel(
            name="Rdi",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("last_modified", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "hhs",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.IntegerField(), help_text="List of HH primary key for this RDI", size=None
                    ),
                ),
                (
                    "inds",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.IntegerField(),
                        help_text="List of IND primary key for this RDI. Empty if HH is set",
                        size=None,
                    ),
                ),
                (
                    "program",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="country_workspace.program"),
                ),
            ],
            options={
                "verbose_name_plural": "Rdi",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="SyncLog",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("last_modified", models.DateTimeField(auto_now=True)),
                ("object_id", models.PositiveIntegerField(blank=True, null=True)),
                ("last_update_date", models.DateTimeField(blank=True, null=True)),
                ("last_id", models.CharField(max_length=255, null=True)),
                ("data", models.JSONField(blank=True, default=dict)),
                (
                    "content_type",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="contenttypes.contenttype"),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Area",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("hope_id", models.CharField(editable=False, max_length=200, unique=True)),
                ("name", models.CharField(max_length=255)),
                ("p_code", models.CharField(blank=True, max_length=32, null=True, verbose_name="P Code")),
                ("valid_from", models.DateTimeField(auto_now_add=True, null=True)),
                ("valid_until", models.DateTimeField(blank=True, null=True)),
                ("extras", models.JSONField(blank=True, default=dict)),
                ("lft", models.PositiveIntegerField(editable=False)),
                ("rght", models.PositiveIntegerField(editable=False)),
                ("tree_id", models.PositiveIntegerField(db_index=True, editable=False)),
                ("level", models.PositiveIntegerField(editable=False)),
                (
                    "parent",
                    mptt.fields.TreeForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="country_workspace.area",
                        verbose_name="Parent",
                    ),
                ),
                (
                    "area_type",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="country_workspace.areatype"),
                ),
            ],
            options={
                "verbose_name_plural": "Areas",
                "ordering": ("name",),
                "constraints": [
                    models.UniqueConstraint(
                        condition=models.Q(("p_code", ""), _negated=True),
                        fields=("p_code",),
                        name="unique_area_p_code_not_blank",
                    )
                ],
            },
        ),
        migrations.AlterUniqueTogether(
            name="batch",
            unique_together={("import_date", "name")},
        ),
        migrations.CreateModel(
            name="UserRole",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("last_modified", models.DateTimeField(auto_now=True)),
                ("expires", models.DateField(blank=True, null=True)),
                (
                    "country_office",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="country_workspace.office"),
                ),
                ("group", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="auth.group")),
                (
                    "program",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="country_workspace.program",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="roles", to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(
                        fields=("user", "country_office", "group"), name="country_workspace_userrole_unique_role"
                    )
                ],
            },
        ),
    ]
