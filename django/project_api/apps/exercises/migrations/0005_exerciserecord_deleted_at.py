# Generated by Django 3.2.12 on 2023-01-16 11:10

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("exercises", "0004_auto_20230102_0925"),
    ]

    operations = [
        migrations.AddField(
            model_name="exerciserecord",
            name="deleted_at",
            field=models.DateTimeField(null=True),
        ),
    ]
