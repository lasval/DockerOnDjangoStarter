# Generated by Django 3.2.12 on 2022-11-28 11:05

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0005_user_app_push"),
    ]

    operations = [
        migrations.RenameField(
            model_name="user",
            old_name="app_push",
            new_name="push_notification",
        ),
    ]
