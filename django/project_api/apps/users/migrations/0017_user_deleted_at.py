# Generated by Django 3.2.12 on 2023-01-31 16:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0016_phoneverification_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="deleted_at",
            field=models.DateTimeField(null=True),
        ),
    ]
