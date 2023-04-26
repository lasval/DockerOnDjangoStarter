# Generated by Django 3.2.12 on 2022-12-12 10:10

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0009_alter_user_device_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="emailverification",
            name="type",
            field=models.CharField(
                choices=[
                    ("sign_up", "회원가입"),
                    ("password_change", "비밀번호변경"),
                    ("withdraw", "회원탈퇴"),
                ],
                default=1,
                max_length=20,
                verbose_name="인증 타입",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="loginlink",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="login_link",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]