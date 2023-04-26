# Generated by Django 3.2.12 on 2022-11-23 13:35

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("commons", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
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
                    "password",
                    models.CharField(max_length=128, verbose_name="password"),
                ),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        verbose_name="date joined",
                    ),
                ),
                ("user_code", models.CharField(max_length=64, unique=True)),
                (
                    "phone",
                    models.CharField(
                        blank=True,
                        max_length=20,
                        null=True,
                        verbose_name="연락처(휴대폰번호)",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        blank=True,
                        max_length=150,
                        null=True,
                        verbose_name="유저명(닉네임)",
                    ),
                ),
                (
                    "gender",
                    models.CharField(
                        blank=True,
                        choices=[("M", "남자"), ("F", "여자"), ("N", "선택 안함")],
                        max_length=1,
                        null=True,
                        verbose_name="성별",
                    ),
                ),
                (
                    "height",
                    models.IntegerField(blank=True, null=True, verbose_name="키"),
                ),
                (
                    "weight",
                    models.IntegerField(blank=True, null=True, verbose_name="몸무게"),
                ),
                (
                    "birthdate",
                    models.DateField(blank=True, null=True, verbose_name="생년월일"),
                ),
                (
                    "agree_to_ad",
                    models.BooleanField(default=False, verbose_name="광고성 수신동의 여부"),
                ),
                (
                    "profile_image_url",
                    models.URLField(max_length=255, verbose_name="프로필 이미지"),
                ),
                (
                    "country_code",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="commons.countrycode",
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.Group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.Permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="EmailVerification",
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
                    "email",
                    models.EmailField(max_length=254, verbose_name="이메일"),
                ),
                (
                    "auth_check",
                    models.BooleanField(default=False, verbose_name="인증 여부"),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="LoginLink",
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
                    "type",
                    models.CharField(
                        choices=[("A", "애플"), ("G", "구글"), ("E", "이메일")],
                        max_length=5,
                        verbose_name="타입",
                    ),
                ),
                (
                    "link_id",
                    models.CharField(
                        blank=True,
                        max_length=200,
                        null=True,
                        verbose_name="링크 아이디",
                    ),
                ),
                (
                    "link_email",
                    models.EmailField(
                        blank=True,
                        max_length=254,
                        null=True,
                        unique=True,
                        verbose_name="링크 이메일",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="user",
            constraint=models.UniqueConstraint(
                fields=("username",), name="unique_username"
            ),
        ),
    ]