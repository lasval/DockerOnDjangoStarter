# Generated by Django 3.2.12 on 2023-01-17 17:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("commons", "0004_auto_20230103_0807"),
        ("users", "0014_rename_phone_phoneverification_phone_number"),
    ]

    operations = [
        migrations.AddField(
            model_name="phoneverification",
            name="country_code",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="commons.countrycode",
                verbose_name="국가 코드",
            ),
            preserve_default=False,
        ),
    ]