import binascii

from django.db import models
from django.utils.translation import gettext_lazy as _


class UploadedImage(models.Model):
    """
    API를 통해 S3로 업로드한 이미지에 대한 정보를 저장하기 위한 모델
    - 이 모델을 사용한 View를 통해 이미지 업로드
    """

    class Meta:
        verbose_name = "이미지 파일 등록"
        verbose_name_plural = "이미지 파일 등록"

    def upload_path(instance, filename):
        import os
        from random import randint

        from django.utils.timezone import now

        filename_base, filename_ext = os.path.splitext(filename)
        filename_crc = format(binascii.crc32(filename_base.encode()), "x")

        return "uploaded-images/%s/A%s%s" % (
            now().strftime("%Y%m%d"),
            str(randint(10000000, 99999999)) + "-" + filename_crc,
            filename_ext,
        )

    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    image = models.ImageField(
        upload_to=upload_path, editable=True, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)


class AppVersion(models.Model):
    class DeviceType(models.TextChoices):
        AOS = "aos", "Android"
        IOS = "ios", "IOS"

    class ServerType(models.TextChoices):
        DEV = "dev", "Dev"
        LIVE = "live", "Live"

    device_type = models.CharField(
        verbose_name="기기 OS 타입", max_length=3, choices=DeviceType.choices
    )
    server_type = models.CharField(
        verbose_name="서버 타입", max_length=5, choices=ServerType.choices
    )
    version = models.CharField(verbose_name="최신 버전", max_length=10)
    force_update = models.BooleanField(verbose_name="강제 업데이트 여부", default=False)
    msg = models.CharField(verbose_name="강제 업데이트시 얼럿 메시지", max_length=100)
    store_url = models.CharField(verbose_name="스토어 URL", max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)


class CountryCode(models.Model):
    country_en_name = models.CharField(verbose_name="영문 국가명", max_length=100)
    country_ko_name = models.CharField(verbose_name="한글 국가명", max_length=100)
    code = models.CharField(verbose_name="국가 코드", max_length=10)
