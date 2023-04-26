# models.py in the users Django app
import binascii

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class LoginType(models.TextChoices):
    """로그인 타입"""

    APPLE = "A", "애플"
    GOOGLE = "G", "구글"
    EMAIL = "E", "이메일"
    DELETE = "D", "삭제"


class DeviceType(models.TextChoices):
    """디바이스 타입"""

    IOS = "ios", "IOS"
    AOS = "aos", "Android"


class Gender(models.TextChoices):
    """성별"""

    MALE = "M", "남자"
    FEMALE = "F", "여자"
    NOT_SELECTED = "N", "선택 안함"
    DELETE = "D", "삭제"


class EmailVerificationType(models.TextChoices):
    """성별"""

    SING_UP = "sign_up", "회원가입"
    PASSWORD_CHANGE = "password_change", "비밀번호변경"
    WITHDRAW = "withdraw", "회원탈퇴"


class UserManager(BaseUserManager):
    """
    기존 User를 User(=CustomUser)로 사용하기 위해 UserManager를 오버라이드해주는 부분
    """

    def create_user(self, user_code, username, password=None):
        """
        Creates and saves a User with the given type, email and password.
        """

        user = self.model(
            user_code=user_code,
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        user_code,
        username=None,
        password=None,
    ):
        """
        Creates and saves a superuser with the given type, email and password.
        """
        user = self.create_user(
            user_code=user_code,
            username=username,
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    """
    User = 계정 (커스텀 유저 모델)
    (DRF에서 사용하는 유저를 기반으로 필드를 원하는대로 만들어서 사용하기 위함)
    """

    first_name = None
    last_name = None
    email = None
    user_code = models.CharField(max_length=64, unique=True)
    phone = models.CharField(
        verbose_name="연락처(휴대폰번호)",
        max_length=20,
        null=True,
        blank=True,
    )
    country_code = models.ForeignKey(
        "commons.CountryCode",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    username = models.CharField(
        verbose_name="회원명",
        max_length=150,
        unique=False,
        null=True,
        blank=True,
    )
    nickname = models.CharField(
        verbose_name="닉네임",
        max_length=150,
        unique=True,
        null=True,
        blank=True,
    )
    gender = models.CharField(
        verbose_name="성별",
        max_length=1,
        choices=Gender.choices,
        null=True,
        blank=True,
    )
    height = models.PositiveSmallIntegerField(
        verbose_name="키",
        null=True,
        blank=True,
    )
    weight = models.PositiveSmallIntegerField(
        verbose_name="몸무게",
        null=True,
        blank=True,
    )
    birthdate = models.DateField(
        verbose_name="생년월일",
        null=True,
        blank=True,
    )
    device_type = models.CharField(
        verbose_name="디바이스 타입",
        max_length=5,
        choices=DeviceType.choices,
    )
    agree_to_ad = models.BooleanField(
        verbose_name="광고성 수신동의 여부",
        default=False,
    )
    push_notification = models.BooleanField(
        verbose_name="앱푸시 온오프",
        default=True,
    )
    profile_image_url = models.URLField(
        verbose_name="프로필 이미지",
        max_length=255,
    )
    deleted_at = models.DateTimeField(null=True)
    objects = UserManager()
    USERNAME_FIELD = "user_code"
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"USER({self.id}), Email : {self.email}"

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_superuser

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # simplest possible answer: Yes, always
        return True

    # class Meta:
    # unique_together = ["user_type", "phone"]
    # 유저 타입별로 phone번호가 유니크하도록 처리
    # constraints = [
    #     models.UniqueConstraint(
    #         fields=["username"],
    #         name="unique_username",
    #     ),
    # ]


class LoginLink(models.Model):
    """
    소셜/이메일 연동점 모델
    """

    type = models.CharField(
        verbose_name="타입",
        max_length=5,
        choices=LoginType.choices,
    )
    link_id = models.CharField(
        verbose_name="링크 아이디", max_length=200, null=True, blank=True
    )
    link_email = models.EmailField(verbose_name="링크 이메일", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="login_link",
    )

    # 두 필드끼리 연관하여 Unique 제약을 주는 경우 사용
    class Meta:
        # unique_together = ["user_type", "phone"]
        # 유저 타입별로 phone번호가 유니크하도록 처리
        constraints = [
            models.UniqueConstraint(
                fields=["type", "link_email"], name="unique_link_email"
            ),
        ]


class EmailVerification(models.Model):
    """
    이메일 인증 모델
    """

    type = models.CharField(
        verbose_name="인증 타입",
        max_length=20,
        choices=EmailVerificationType.choices,
    )
    code = models.CharField(
        verbose_name="인증 코드",
        max_length=10,
    )
    email = models.EmailField(verbose_name="이메일")
    auth_check = models.BooleanField(
        verbose_name="인증 여부",
        default=False,
    )
    created_at = models.DateTimeField(auto_now_add=True)


class UserProfileUploadedImage(models.Model):
    """
    API를 통해 S3로 업로드한 이미지에 대한 정보를 저장하기 위한 모델
    - 이 모델을 사용한 View를 통해 이미지 업로드
    """

    def upload_path(instance, filename):
        import os
        from random import randint

        from django.utils.timezone import now

        filename_base, filename_ext = os.path.splitext(filename)
        filename_crc = format(binascii.crc32(filename_base.encode()), "x")

        return "uploaded-images/user-profile-images/%s/U%s%s" % (
            now().strftime("%Y%m%d"),
            str(randint(10000000, 99999999)) + "-" + filename_crc,
            filename_ext,
        )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(
        upload_to=upload_path, editable=True, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)


class PhoneVerification(models.Model):
    """
    글로벌 핸드폰 인증 모델
    """

    code = models.CharField(
        verbose_name="인증 코드",
        max_length=10,
    )
    country_code = models.ForeignKey(
        "commons.CountryCode",
        on_delete=models.CASCADE,
        verbose_name="국가 코드",
    )
    phone_number = models.CharField(
        verbose_name="핸드폰 번호",
        max_length=20,
    )
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        verbose_name="유저",
    )
    auth_check = models.BooleanField(
        verbose_name="인증 여부",
        default=False,
    )
    created_at = models.DateTimeField(auto_now_add=True)
