# Generated by Django 5.1.2 on 2024-10-23 05:40

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("versioning", "0001_initial"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Version",
            new_name="Script",
        ),
    ]
