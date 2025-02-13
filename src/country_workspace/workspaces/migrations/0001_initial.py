# Generated by Django 5.1.3 on 2024-12-01 19:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("country_workspace", "0001_initial"),
        ("hope_flex_fields", "0013_fielddefinition_validated_alter_datachecker_id_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="CountryAsyncJob",
            fields=[],
            options={
                "verbose_name": "Background Job",
                "verbose_name_plural": "Background Jobs",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("country_workspace.asyncjob",),
        ),
        migrations.CreateModel(
            name="CountryBatch",
            fields=[],
            options={
                "verbose_name": "Country Batch",
                "verbose_name_plural": "Country Batches",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("country_workspace.batch",),
        ),
        migrations.CreateModel(
            name="CountryHousehold",
            fields=[],
            options={
                "verbose_name": "Country Household",
                "verbose_name_plural": "Country Households",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("country_workspace.household",),
        ),
        migrations.CreateModel(
            name="CountryIndividual",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("country_workspace.individual",),
        ),
        migrations.CreateModel(
            name="CountryProgram",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("country_workspace.program",),
        ),
        migrations.CreateModel(
            name="CountryChecker",
            fields=[
                (
                    "datachecker_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="hope_flex_fields.datachecker",
                    ),
                ),
                (
                    "country_office",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="country_workspace.office"),
                ),
            ],
            bases=("hope_flex_fields.datachecker",),
        ),
    ]
