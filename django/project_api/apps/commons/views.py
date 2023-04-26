from project_api.utils import BadRequestError
from commons.models import AppVersion, CountryCode
from django_filters.rest_framework.backends import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from django.db.models import F
from django.template.defaultfilters import filesizeformat
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy

from .serializers import (
    AppVersionSerializer,
    CountryCodeSerializer,
    TermsOfServiceSerializer,
    UploadedImageSerializer,
)


class CommonImageUploadView(generics.CreateAPIView):
    """
    post: 각 이미지 업로드뷰에서 상속하여 사용할 이미지 업로드 클래스(뷰)

    - 현재는 기본이 되는 해당 뷰도 API로 노출되도록 처리
    - 추후 화면에 따라 이미지 파일 크기를 다르게 처리하려면 해당 뷰 클래스를 상속받은 새로운 뷰로 API를 만들어 사용
    - 기본 이미지 파일 사이즈 제약은 5MB
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UploadedImageSerializer
    parser_classes = (MultiPartParser,)
    MAX_SIZE = 5242880  # 기본 제약은 5MB = 5 * 1024 * 1024 = 5242880

    def set_max_size(self, max_size):
        self.MAX_SIZE = max_size

    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        image = validated_data.get("image", None)
        if image is None:
            return BadRequestError(
                message=ugettext_lazy("이미지가 존재하지 않습니다."),
            )

        MAX_SIZE = self.MAX_SIZE
        max_size_str = filesizeformat(MAX_SIZE)
        if image.size >= MAX_SIZE:
            return BadRequestError(
                message=ugettext_lazy(f"이미지의 크기가 {max_size_str}를 넘습니다."),
            )

        serializer.save(user=self.request.user)


class AppVersionView(generics.ListAPIView):
    """
    get: 스토어 최신 버전 조회

    - store_url을 바로 호출하면 디바이스 상에서 스토어가 열림
        - 예시값:
            - Android: `market://details?id=com.popprika.project` 형태
            - iOS: `itms-apps://itunes.apple.com/app/id1526117893` 형태
    - device_type 쿼리 파라미터로 원하는 device_type에 대한 값만 조회(필터링) 가능
        - `?device_type=aos`
        - `?device_type=ios`
        - aos는 안드로이드 값
        - ios는 애플 값입니다.
    - server_type 쿼리 파라미터로 원하는 server_type에 대한 값만 조회(필터링) 가능
        - `?server_type=dev`
        - `?server_type=live`
        - dev는 개발환경 값
        - live는 라이브환경 값입니다.
    - 리스트 형태로 리턴되기 떄문에 필터링 없이 선택해서 사용해도 무관
    """

    permission_classes = [permissions.AllowAny]
    pagination_class = None
    serializer_class = AppVersionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        "device_type",
        "server_type",
    ]
    queryset = AppVersion.objects.all()


class TermsOfService(APIView):
    """
    get: 약관동의 항목별 정보 조회

    - 초기 회원가입시 약관동의 항목별 정보이다.

    """

    permission_classes = [permissions.AllowAny]

    @method_decorator(
        name="get",
        decorator=swagger_auto_schema(
            request_body=None,
            responses={200: TermsOfServiceSerializer()},
        ),
    )
    def get(self, request):
        agree_all_title = "I agree to all the following"
        agree_all_desc = "I agree to the Terms of Service, useof collected information, third party usage, promotion & marketing usage."
        terms_title = "Consent to Terms of Service"
        terms_option = "(mandatory)"
        terms_detail = """
            testtesttesttesttesttesttesttesttesttesttesttesttest
            testtesttesttesttesttesttesttesttesttesttesttesttest
            testtesttesttesttesttesttesttesttesttesttesttesttest
            testtesttesttesttesttesttesttesttesttesttesttesttest
            testtesttesttesttesttesttesttesttesttesttesttesttest
            testtesttesttesttesttesttesttesttesttesttesttesttest
            testtesttesttesttesttesttesttesttesttesttesttesttest
            testtesttesttesttesttesttesttesttesttesttesttesttest
            testtesttesttesttesttesttesttesttesttesttesttesttest
        """
        private_title = "Guide for private information collection and use"
        private_option = "(mandatory)"
        private_detail = """
            testtesttesttesttesttesttesttesttesttesttesttesttest
            testtesttesttesttesttesttesttesttesttesttesttesttest
            testtesttesttesttesttesttesttesttesttesttesttesttest
            testtesttesttesttesttesttesttesttesttesttesttesttest
            testtesttesttesttesttesttesttesttesttesttesttesttest
            testtesttesttesttesttesttesttesttesttesttesttesttest
            testtesttesttesttesttesttesttesttesttesttesttesttest
            testtesttesttesttesttesttesttesttesttesttesttesttest
            testtesttesttesttesttesttesttesttesttesttesttesttest
            testtesttesttesttesttesttesttesttesttesttesttesttest
        """
        ad_title = "I want to receive promotional e-mails"
        ad_option = "(optional)"

        terms_serializer = TermsOfServiceSerializer(
            {
                "agree_all_title": agree_all_title,
                "agree_all_desc": agree_all_desc,
                "terms_title": terms_title,
                "terms_option": terms_option,
                "terms_detail": terms_detail,
                "private_title": private_title,
                "private_option": private_option,
                "private_detail": private_detail,
                "ad_title": ad_title,
                "ad_option": ad_option,
            }
        )
        return Response(status=status.HTTP_200_OK, data=terms_serializer)


class CountryCodeView(APIView):
    """
    get: 국가별 번호 코드 조회

    - 국가별 번호 코드 조회이다.
    - Header에 Accept-Language
        - `ko`, `en`의 종류에 따라 국가 이름 출력
        - Default = `en`
    """

    permission_classes = [permissions.IsAuthenticated]

    @method_decorator(
        name="get",
        decorator=swagger_auto_schema(
            request_body=None,
            responses={200: CountryCodeSerializer(many=True)},
        ),
    )
    def get(self, request):
        accept_language = request.headers.get("Accept-Language", None)

        if accept_language == "ko":
            country_codes = (
                CountryCode.objects.all()
                .values("id", "country_ko_name", "code")
                .annotate(name=F("country_ko_name"))
                .order_by("id")
            )
        elif accept_language == "en":
            country_codes = (
                CountryCode.objects.all()
                .values("id", "country_en_name", "code")
                .annotate(name=F("country_en_name"))
                .order_by("id")
            )
        else:
            country_codes = (
                CountryCode.objects.all()
                .values("id", "country_en_name", "code")
                .annotate(name=F("country_en_name"))
                .order_by("id")
            )

        country_code_list = []
        for country_code in country_codes:
            country_code_list.append(
                {
                    "id": country_code["id"],
                    "name": country_code["name"],
                    "code": country_code["code"],
                }
            )
        country_code_serializer = CountryCodeSerializer(country_code_list, many=True)
        return Response(status=status.HTTP_200_OK, data=country_code_serializer.data)
