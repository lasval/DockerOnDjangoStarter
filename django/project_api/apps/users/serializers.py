import re
from datetime import datetime

from project_api.custom_password_validation import (
    validate_password as custom_validate_password,
)
from project_api.utils import StandardException
from commons.models import CountryCode
from emoji import core
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from django.contrib.auth.password_validation import validate_password
from django.utils.translation import ugettext_lazy

from .models import (
    DeviceType,
    EmailVerificationType,
    Gender,
    LoginLink,
    LoginType,
    User,
    UserProfileUploadedImage,
)
from .utils import generate_unique_user_code


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("email", "password", "password2", "nickname")

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Password does not match."})

        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            nickname=validated_data.get("nickname", None),
            email=validated_data["email"],
            user_code=generate_unique_user_code(),
            last_login=datetime.now(),
        )

        user.set_password(validated_data["password"])
        user.save()

        return user


class EmailVerificationSendSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=EmailVerificationType, required=True)
    email = serializers.EmailField(required=False)

    def validate(self, attrs):
        if (
            LoginLink.objects.filter(
                link_email=attrs["email"],
                type=LoginType.EMAIL.value,
                user__deleted_at__isnull=True,
            ).exists()
            is True
            and attrs["type"] == "sign_up"
        ):
            raise StandardException(
                400,
                ugettext_lazy(
                    "This account is registered by social authentication login already"
                ),
            )
        elif (
            LoginLink.objects.filter(
                link_email=attrs["email"],
                type=LoginType.EMAIL.value,
                user__deleted_at__isnull=True,
            ).exists()
            is False
            and attrs["type"] == "password_change"
        ):
            raise StandardException(
                400,
                ugettext_lazy("Unregistered E-mail"),
            )

        return attrs


class EmailVerificationConfirmSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=EmailVerificationType, required=True)
    email = serializers.EmailField(required=False)
    code = serializers.CharField(required=True)

    def validate(self, attrs):
        if (
            LoginLink.objects.filter(
                link_email=attrs["email"],
                type=LoginType.EMAIL.value,
                user__deleted_at__isnull=True,
            ).exists()
            and type == "sign_up"
        ):
            raise StandardException(
                422,
                ugettext_lazy("Email already exists"),
            )
        return attrs


class EamilRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password1 = serializers.CharField(
        required=True, validators=[custom_validate_password]
    )
    password2 = serializers.CharField(required=True)
    device_type = serializers.ChoiceField(choices=DeviceType, required=True)
    agree_to_ad = serializers.BooleanField(required=False, default=False)

    def validate(self, attrs):
        if LoginLink.objects.filter(
            link_email=attrs["email"],
            type=LoginType.EMAIL.value,
            user__deleted_at__isnull=True,
        ).exists():
            raise StandardException(
                422,
                ugettext_lazy("Email already exists"),
            )

        if attrs["password1"] != attrs["password2"]:
            raise StandardException(
                400,
                ugettext_lazy("Password does not match"),
            )

        return attrs


class EmailStandardSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)


class NicknameCheckSerializer(serializers.Serializer):
    nickname = serializers.CharField(required=True)

    def validate(self, attrs):
        ## TODO 현재는 영문 숫자 조합으로만 닉네임 설정 가능
        ## 이모지 사용 불가능
        if (
            not re.match("[a-zA-Z0-9]+", attrs["nickname"])
            and core.emoji_count(attrs["nickname"]) == 0
        ):
            raise StandardException(
                400,
                ugettext_lazy(
                    "Emoji or special characters cannot be used as nicknames"
                ),
            )

        if User.objects.filter(
            nickname=attrs["nickname"], deleted_at__isnull=True
        ).exists():
            return StandardException(
                400,
                ugettext_lazy("Duplicate nickname"),
            )

        return attrs


class NicknameCheckResponseSerializer(serializers.Serializer):
    message = serializers.CharField(required=False)


class ProfileEditSerializer(serializers.Serializer):
    nickname = serializers.CharField(required=False)
    gender = serializers.ChoiceField(choices=Gender, required=False)
    height = serializers.IntegerField(required=False)
    weight = serializers.IntegerField(required=False)
    birthdate = serializers.DateField(required=False)


class IDAndTokenResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    token = serializers.CharField(required=False)


class LoginUserDataResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    token = serializers.CharField(allow_null=True, required=False)
    nickname = serializers.CharField(allow_null=True, required=False)
    login_type = serializers.CharField(required=False)
    email = serializers.EmailField(allow_null=True, required=False)
    gender = serializers.ChoiceField(choices=Gender, allow_null=True, required=False)
    height = serializers.IntegerField(allow_null=True, required=False)
    weight = serializers.IntegerField(allow_null=True, required=False)
    birthdate = serializers.DateField(allow_null=True, required=False)
    profile_image_url = serializers.URLField(allow_null=True, required=False)


class SocialRegistrationSerializer(serializers.Serializer):
    social_type = serializers.ChoiceField(choices=LoginType, required=True)
    social_id = serializers.CharField(required=True)
    social_email = serializers.EmailField(required=True)
    device_type = serializers.ChoiceField(choices=DeviceType, required=True)
    agree_to_ad = serializers.BooleanField(required=False, default=False)


class SocialLoginSerializer(serializers.Serializer):
    social_type = serializers.ChoiceField(choices=LoginType, required=True)
    id_token = serializers.CharField(required=False)
    social_id = serializers.CharField(required=True)
    social_email = serializers.EmailField(required=True)


class PasswordChangeSerializer(serializers.Serializer):
    type = serializers.CharField(required=True)
    email = serializers.EmailField(required=False)
    password1 = serializers.CharField(
        required=True, validators=[custom_validate_password]
    )
    password2 = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs["password1"] != attrs["password2"]:
            raise StandardException(
                400,
                ugettext_lazy("Password does not match"),
            )

        return attrs


class SettingDataResponseSerializer(serializers.Serializer):
    push_notifications = serializers.BooleanField(required=False)
    google_authenticator = serializers.BooleanField(required=False)
    receive_promotional_email = serializers.BooleanField(required=False)


class UserSimpleSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nickname = serializers.CharField()


class PasswordConfirmSerializer(serializers.Serializer):
    password = serializers.CharField(required=True)


class ProfileImageS3UploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfileUploadedImage
        fields = ("image",)
        extra_kwargs = {
            "image": {"required": True},
        }


class ProfileImageChangeSerializer(serializers.Serializer):
    image = serializers.URLField(required=True)


class PhoneVerificationSendSerializer(serializers.Serializer):
    country_code_id = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True)

    def validate(self, attrs):
        if not CountryCode.objects.filter(id=attrs["country_code_id"]).exists():
            raise StandardException(
                400,
                ugettext_lazy("country code does not exists"),
            )

        return attrs


class PhoneVerificationConfirmSerializer(serializers.Serializer):
    country_code_id = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True)
    code = serializers.CharField(required=True)

    def validate(self, attrs):
        if not CountryCode.objects.filter(id=attrs["country_code_id"]).exists():
            raise StandardException(
                400,
                ugettext_lazy("country code does not exists"),
            )

        return attrs
