# Generated by Django 5.1.1 on 2024-10-11 09:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("country_workspace", "0001_initial"),
        ("hope_flex_fields", "0007_create_default_fields"),
    ]

    operations = [
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
