from rest_framework import serializers

from .models import AppVersion, UploadedImage


class UploadedImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedImage
        fields = ("image",)
        extra_kwargs = {
            "image": {"required": True},
        }


class AppVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppVersion
        fields = (
            "device_type",
            "server_type",
            "version",
            "force_update",
            "msg",
            "store_url",
            "created_at",
        )


class TermsOfServiceSerializer(serializers.Serializer):
    agree_all_title = serializers.CharField(required=False)
    agree_all_desc = serializers.CharField(required=False)
    terms_title = serializers.CharField(required=False)
    terms_option = serializers.CharField(required=False)
    terms_detail = serializers.CharField(required=False)
    private_title = serializers.CharField(required=False)
    private_option = serializers.CharField(required=False)
    private_detail = serializers.CharField(required=False)
    ad_title = serializers.CharField(required=False)
    ad_option = serializers.CharField(required=False)


class CountryCodeSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False)
    code = serializers.CharField(required=False)
