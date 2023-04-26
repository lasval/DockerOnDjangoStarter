# Generated by Django 3.2.12 on 2023-01-03 08:07

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("commons", "0003_alter_appversion_device_type"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="countrycode",
            name="country",
        ),
        migrations.AddField(
            model_name="countrycode",
            name="country_en_name",
            field=models.CharField(default=1, max_length=100, verbose_name="영문 국가명"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="countrycode",
            name="country_ko_name",
            field=models.CharField(default=1, max_length=100, verbose_name="한글 국가명"),
            preserve_default=False,
        ),
    ]
