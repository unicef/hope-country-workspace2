# Generated by Django 5.1.2 on 2024-11-25 09:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("country_workspace", "0002_koboasset_kobosyncjob_kobosubmission"),
    ]

    operations = [
        migrations.AddField(
            model_name="koboasset",
            name="programs",
            field=models.ManyToManyField(to="country_workspace.program"),
        ),
    ]
