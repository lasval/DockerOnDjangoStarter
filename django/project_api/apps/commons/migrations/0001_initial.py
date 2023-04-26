# Generated by Django 3.2.12 on 2022-11-23 13:35

import commons.models

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AppVersion",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "device_type",
                    models.CharField(
                        choices=[("aos", "Android"), ("ios", "iOS")],
                        max_length=3,
                        verbose_name="기기 OS 타입",
                    ),
                ),
                (
                    "server_type",
                    models.CharField(
                        choices=[("dev", "Dev"), ("live", "Live")],
                        max_length=5,
                        verbose_name="서버 타입",
                    ),
                ),
                (
                    "version",
                    models.CharField(max_length=10, verbose_name="최신 버전"),
                ),
                (
                    "force_update",
                    models.BooleanField(default=False, verbose_name="강제 업데이트 여부"),
                ),
                (
                    "msg",
                    models.CharField(max_length=100, verbose_name="강제 업데이트시 얼럿 메시지"),
                ),
                (
                    "store_url",
                    models.CharField(max_length=255, verbose_name="스토어 URL"),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="CountryCode",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "country",
                    models.CharField(max_length=100, verbose_name="국가명"),
                ),
                (
                    "code",
                    models.CharField(max_length=10, verbose_name="국가 코드"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="UploadedImage",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "image",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to=commons.models.UploadedImage.upload_path,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "이미지 파일 등록",
                "verbose_name_plural": "이미지 파일 등록",
            },
        ),
    ]
