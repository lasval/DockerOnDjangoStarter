# Generated by Django 3.2.12 on 2023-01-17 14:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0012_auto_20230102_0925"),
    ]

    operations = [
        migrations.CreateModel(
            name="PhoneVerification",
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
                    "code",
                    models.CharField(max_length=10, verbose_name="인증 코드"),
                ),
                (
                    "phone",
                    models.CharField(max_length=20, verbose_name="핸드폰 번호"),
                ),
                (
                    "auth_check",
                    models.BooleanField(default=False, verbose_name="인증 여부"),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
