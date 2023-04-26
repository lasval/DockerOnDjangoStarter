import os
from datetime import datetime, timedelta

from project_api.utils import (
    StandardError,
    UnprocessableEntityError,
    aws_email_single_send,
    aws_sms_single_send,
    get_random_number_code,
    get_serilaizer_check,
)
from commons.models import CountryCode
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from users.serializers import (
    EamilRegistrationSerializer,
    EmailStandardSerializer,
    EmailVerificationConfirmSerializer,
    EmailVerificationSendSerializer,
    IDAndTokenResponseSerializer,
    LoginUserDataResponseSerializer,
    NicknameCheckResponseSerializer,
    NicknameCheckSerializer,
    PasswordChangeSerializer,
    PasswordConfirmSerializer,
    PhoneVerificationConfirmSerializer,
    PhoneVerificationSendSerializer,
    ProfileEditSerializer,
    ProfileImageChangeSerializer,
    ProfileImageS3UploadSerializer,
    SettingDataResponseSerializer,
    SocialLoginSerializer,
    SocialRegistrationSerializer,
)

from django.db import IntegrityError, transaction
from django.template.defaultfilters import filesizeformat
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy

from .models import EmailVerification, LoginLink, LoginType, PhoneVerification, User
from .utils import (
    generate_unique_user_code,
    get_login_link_data,
    get_user_link_with_token,
    google_auth,
    verification_time_limit,
)


class EmailVerificationSend(APIView):
    """
    post: 이메일 인증번호 발송 API

    - 이메일 인증번호 발송
    - type
        - 회원가입시 `"type":"sign_up"`
        - 비밀번호 변경시(FindPassword) `"type":"password_change"`
        - 회원탈퇴시 `"type":"withdraw"`

    - email
        - 회원가입시 = 필수
        - 비밀번호 변경시(FindPassword) = 필수
        - 회원탈퇴시 = X

    - 회원탈퇴시
        - HTTP Header에 api-key Token 필요
            key: Authorization, value: Token [토큰값] (예시: Authorization: Token c5a4e25a7c5d8dc545c8d10740bfe655429c129b)

    - dev환경에서는 인증번호가 `{"code":"111111111"}`형식으로 response 출력
    """

    permission_classes = [permissions.AllowAny]

    @method_decorator(
        name="post",
        decorator=swagger_auto_schema(
            request_body=EmailVerificationSendSerializer(),
            responses={200: ""},
        ),
    )
    def post(self, request):
        serializer = get_serilaizer_check(EmailVerificationSendSerializer, request.data)

        type = serializer.data.get("type", None)
        email = serializer.data.get("email", None)

        if type == "withdraw":
            link = get_user_link_with_token(request.auth)
            email = link.link_email

        subject = "[project]Email Verification Code"
        code = get_random_number_code(8)
        body_html = f"{code}"

        with transaction.atomic():
            EmailVerification.objects.create(
                code=code,
                email=email,
                type=type,
            )

        if os.environ.get("ENVIRONMENT") == "production":
            aws_email_single_send(
                email,
                subject,
                body_html,
            )
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_200_OK, data={"code": f"{code}"})
        # 재전송 제한 시간 예시
        # resend_cooltime = datetime.now() - timedelta(seconds=30)
        # prev = EmailVerification.objects.filter(
        #     email=email,
        #     created_at__gt=resend_cooltime,
        # ).order_by("-created_at").first()
        # if prev is None:
        #     EmailVerification.objects.create(
        #         code=code,
        #         email=email,
        #     )
        #     return Response(status=status.HTTP_200_OK)
        # else:
        # return UnprocessableEntityError(
        #     message="wait 30 seconds",
        # )


class EmailVerificationConfirm(APIView):
    """
    post: 이메일 인증번호 확인 API

    - 이메일 인증번호 확인

    - type
        - 회원가입시 `"type":"sign_up"`
        - 비밀번호 변경시(FindPassword) `"type":"password_change"`
        - 회원탈퇴시 `"type":"withdraw"`

    - email
        - 회원가입시 = 필수
        - 비밀번호 변경시(FindPassword) = 필수
        - 회원탈퇴시 = X

    - 회원탈퇴시
        - HTTP Header에 api-key Token 필요
            key: Authorization, value: Token [토큰값] (예시: Authorization: Token c5a4e25a7c5d8dc545c8d10740bfe655429c129b)
    """

    permission_classes = [permissions.AllowAny]

    @method_decorator(
        name="post",
        decorator=swagger_auto_schema(
            request_body=EmailVerificationConfirmSerializer(),
            responses={200: None},
        ),
    )
    def post(self, request):
        serializer = get_serilaizer_check(
            EmailVerificationConfirmSerializer, request.data
        )

        today = datetime.now()

        type = serializer.data.get("type", None)
        code = serializer.data.get("code", None)
        email = serializer.data.get("email", None)

        if type == "withdraw":
            link = get_user_link_with_token(request.auth)
            email = link.link_email

        try:
            email_verification = EmailVerification.objects.get(
                type=type,
                code=code,
                email=email,
                auth_check=False,
                created_at__year=today.year,
                created_at__month=today.month,
                created_at__day=today.day,
            )
        except EmailVerification.DoesNotExist:
            return UnprocessableEntityError(message=ugettext_lazy("Incorrect Code"))

        recent_email_verification = EmailVerification.objects.filter(
            type=type,
            email=email,
            auth_check=False,
            created_at__year=today.year,
            created_at__month=today.month,
            created_at__day=today.day,
        ).order_by("-created_at")

        # 인증 제한 시간 10 분 예시
        intime = datetime.now() - timedelta(minutes=10)
        intime_obj = (
            EmailVerification.objects.filter(email=email, created_at__gte=intime)
            .order_by("-created_at")
            .first()
        )
        return verification_time_limit(
            request,
            intime_obj,
            email_verification,
            recent_email_verification,
        )


class EmailRegistration(APIView):
    """
    post: 이메일 회원가입 API

    - 이메일 회원가입
    - device_type
        - 아이폰 `"device_type":"ios"`
        - 안드로이드 `"device_type":"aos"`
    """

    permission_classes = [permissions.AllowAny]

    @method_decorator(
        name="post",
        decorator=swagger_auto_schema(
            request_body=EamilRegistrationSerializer(),
            responses={201: IDAndTokenResponseSerializer()},
        ),
    )
    def post(self, request):
        serializer = get_serilaizer_check(EamilRegistrationSerializer, request.data)

        email = serializer.data.get("email", None)
        password1 = serializer.data.get("password1", None)
        device_type = serializer.data.get("device_type", None)
        agree_to_ad = serializer.data.get("agree_to_ad", None)

        if not EmailVerification.objects.filter(
            email=email,
            auth_check=True,
            created_at__gte=datetime.now() - timedelta(minutes=30),
        ).exists():
            return UnprocessableEntityError(
                message=ugettext_lazy("Email verification time over")
            )

        with transaction.atomic():
            user = User.objects.create(
                user_code=generate_unique_user_code(),
                device_type=device_type,
                agree_to_ad=agree_to_ad,
            )
            LoginLink.objects.create(
                type=LoginType.EMAIL.value,
                link_id=None,
                link_email=email,
                user_id=user.id,
            )

            user.set_password(password1)
            user.save(update_fields=["password"])

        try:
            token_obj = Token.objects.create(user=user)
        except IntegrityError:
            token_obj = Token.objects.get(user=user)
        token = token_obj.key

        token_serializer = IDAndTokenResponseSerializer({"id": user.id, "token": token})

        return Response(status=status.HTTP_201_CREATED, data=token_serializer.data)


class EmailLogin(APIView):
    """
    post: 이메일 로그인 API

    - 이메일 로그인
    """

    permission_classes = [permissions.AllowAny]

    @method_decorator(
        name="post",
        decorator=swagger_auto_schema(
            request_body=EmailStandardSerializer(),
            responses={200: IDAndTokenResponseSerializer()},
        ),
    )
    def post(self, request):
        serializer = get_serilaizer_check(EmailStandardSerializer, request.data)

        email = serializer.data.get("email", None)
        password = serializer.data.get("password", None)

        # 유저 타입 체크가 완료되면 타입별로 유저 정보를 확인하여 로그인 처리
        try:
            login_link = LoginLink.objects.get(
                link_email=email, type="E", user__deleted_at__isnull=True
            )
            is_password_valid = login_link.user.check_password(password)
        except LoginLink.DoesNotExist:
            return UnprocessableEntityError(
                message=ugettext_lazy("Unregistered E-mail")
            )
        else:
            if not is_password_valid:
                return UnprocessableEntityError(
                    message=ugettext_lazy("Incorrect Password")
                )

            # 해당 유저의 토큰이 존재하면 그대로 리턴, 없으면 새로 만들어 리턴
            try:
                token_obj = Token.objects.create(user=login_link.user)
            except IntegrityError:
                token_obj = Token.objects.get(user=login_link.user)
                token_obj.delete()
                token_obj = Token.objects.create(user=login_link.user)
            token = token_obj.key

            # 유저의 last_login값 업데이트
            login_link.user.last_login = datetime.now()
            login_link.user.save(update_fields=["last_login"])

        token_serializer = IDAndTokenResponseSerializer(
            {"id": login_link.user.id, "token": token}
        )

        return Response(status=status.HTTP_200_OK, data=token_serializer.data)


class EmailLogout(APIView):
    """
    post: 로그아웃 API

    - 로그아웃
    """

    permission_classes = [permissions.IsAuthenticated]

    @method_decorator(
        name="post",
        decorator=swagger_auto_schema(request_body=None, responses={200: ""}),
    )
    def post(self, request):
        try:
            token = Token.objects.get(user=request.user)
        except Token.DoesNotExist:
            try:
                token = Token.objects.create(user=request.user)
            except IntegrityError:
                token = Token.objects.get(user=request.user)
        token.delete()

        return Response(status=status.HTTP_200_OK)


class NicknameCheck(APIView):
    """
    post: 닉네임 중복 체크 API

    - HTTP Header에 api-key Token 필요
        key: Authorization, value: Token [토큰값]
        (예시: Authorization: Token c5a4e25a7c5d8dc545c8d10740bfe655429c129b)
    """

    permission_classes = [permissions.IsAuthenticated]

    @method_decorator(
        name="post",
        decorator=swagger_auto_schema(
            request_body=NicknameCheckSerializer(),
            responses={200: NicknameCheckResponseSerializer()},
        ),
    )
    def post(self, request):
        get_serilaizer_check(NicknameCheckSerializer, request.data)

        data = NicknameCheckResponseSerializer({"message": "Nickname available"})

        return Response(status=status.HTTP_200_OK, data=data.data)


class ProfileEdit(APIView):
    """
    patch: 프로필 수정 API

    - HTTP Header에 api-key Token 필요
        key: Authorization, value: Token [토큰값]
        (예시: Authorization: Token c5a4e25a7c5d8dc545c8d10740bfe655429c129b)

    - 닉네임
    - 성별
        - 남자 `"gender":"M"`
        - 여자 `"gender":"F"`
        - 선택안함 `"gender":"N"`
    - 키
    - 몸무게
    - 생년월일

    필요한 값에 대해서만 넘겨주고 나머지는 포함시키지 않는다.
    """

    permission_classes = [permissions.IsAuthenticated]

    @method_decorator(
        name="patch",
        decorator=swagger_auto_schema(
            request_body=ProfileEditSerializer(), responses={200: ""}
        ),
    )
    def patch(self, request):
        serializer = get_serilaizer_check(ProfileEditSerializer, request.data)

        nickname = serializer.data.get("nickname", None)
        gender = serializer.data.get("gender", None)
        height = serializer.data.get("height", None)
        weight = serializer.data.get("weight", None)
        birthdate = serializer.data.get("birthdate", None)

        if nickname is not None:
            request.user.nickname = nickname
        if gender is not None:
            request.user.gender = gender
        if height is not None:
            request.user.height = height
        if weight is not None:
            request.user.weight = weight
        if birthdate is not None:
            request.user.birthdate = birthdate

        request.user.save()

        return Response(status=status.HTTP_200_OK)


class LoginUserData(APIView):
    """
    get: 로그인한 사용자 데이터 조회

    - HTTP Header에 api-key Token 필요
        key: Authorization, value: Token [토큰값] (예시: Authorization: Token c5a4e25a7c5d8dc545c8d10740bfe655429c129b)
    """

    permission_classes = [permissions.IsAuthenticated]

    @method_decorator(
        name="get",
        decorator=swagger_auto_schema(
            request_body=None,
            responses={200: LoginUserDataResponseSerializer()},
        ),
    )
    def get(self, request):
        user = request.user

        login_link = get_login_link_data(request.user)

        try:
            token = Token.objects.get(user=request.user)
        except Token.DoesNotExist:
            try:
                token = Token.objects.create(user=request.user)
            except IntegrityError:
                token = Token.objects.get(user=request.user)

        login_user_data = LoginUserDataResponseSerializer(
            {
                "id": user.id,
                "token": token.key,
                "nickname": user.nickname,
                "login_type": login_link.type,
                "email": login_link.link_email,
                "gender": user.gender,
                "height": user.height,
                "weight": user.weight,
                "birthdate": user.birthdate,
                "profile_image_url": user.profile_image_url,
            }
        )

        return Response(status=status.HTTP_200_OK, data=login_user_data.data)


class SocialRegistration(APIView):
    """
    post: 소셜 회원가입 API

    - social_type
        - 애플 `"social_type":"A"`
        - 구글 `"social_type":"G"`
    - device_type
        - 아이폰 `"device_type":"ios"`
        - 안드로이드 `"device_type":"aos"`

    """

    permission_classes = [permissions.AllowAny]

    @method_decorator(
        name="post",
        decorator=swagger_auto_schema(
            request_body=SocialRegistrationSerializer(),
            responses={201: IDAndTokenResponseSerializer()},
        ),
    )
    def post(self, request):
        serializer = get_serilaizer_check(SocialRegistrationSerializer, request.data)

        social_type = serializer.data.get("social_type", None)
        social_id = serializer.data.get("social_id", None)
        social_email = serializer.data.get("social_email", None)
        device_type = serializer.data.get("device_type", None)
        agree_to_ad = serializer.data.get("agree_to_ad", None)

        if LoginLink.objects.filter(
            type=social_type,
            link_email=social_email,
            user__deleted_at__isnull=True,
        ).exists():
            return UnprocessableEntityError(
                message=ugettext_lazy("Email already exists")
            )

        if LoginLink.objects.filter(
            link_id=social_id, type=social_type, user__deleted_at__isnull=True
        ).exists():
            return UnprocessableEntityError(
                message=ugettext_lazy("Social already exists")
            )
        with transaction.atomic():
            user = User.objects.create(
                user_code=generate_unique_user_code(),
                device_type=device_type,
                agree_to_ad=agree_to_ad,
            )
            LoginLink.objects.create(
                type=social_type,
                link_id=social_id,
                link_email=social_email,
                user_id=user.id,
                user__deleted_at__isnull=True,
            )

            user.set_password(social_id + social_email)
            user.save(update_fields=["password"])

        try:
            token_obj = Token.objects.create(user=user)
        except IntegrityError:
            token_obj = Token.objects.get(user=user)
        token = token_obj.key

        token_serializer = IDAndTokenResponseSerializer({"id": user.id, "token": token})

        return Response(status=status.HTTP_201_CREATED, data=token_serializer.data)


class SocialLogin(APIView):
    """
    post: 소셜 로그인 API

    - social_type
        - 구글 `"social_type":"G"`
        - 애플 `"social_type":"A"`

    - id_token
        - 구글 소셜 로그인시에만 전달해주시면 됩니다.

    """

    permission_classes = [permissions.AllowAny]

    @method_decorator(
        name="post",
        decorator=swagger_auto_schema(
            request_body=SocialLoginSerializer(),
            responses={200: IDAndTokenResponseSerializer()},
        ),
    )
    def post(self, request):
        serializer = get_serilaizer_check(SocialLoginSerializer, request.data)

        social_type = serializer.data.get("social_type", None)
        social_email = serializer.data.get("social_email", None)
        social_id = serializer.data.get("social_id", None)

        if social_type == LoginType.GOOGLE.value:
            id_token = serializer.data.get("id_token", None)
            google_auth(id_token, social_id)

        try:
            login_link = LoginLink.objects.get(
                link_id=social_id,
                link_email=social_email,
                type=social_type,
                user__deleted_at__isnull=True,
            )
        except LoginLink.DoesNotExist:
            return StandardError(
                status_code=404,
                message=ugettext_lazy("Social does not exists"),
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            token_obj = Token.objects.create(user=login_link.user)
        except IntegrityError:
            token_obj = Token.objects.get(user=login_link.user)
            token_obj.delete()
            token_obj = Token.objects.create(user=login_link.user)
        token = token_obj.key

        token_serializer = IDAndTokenResponseSerializer(
            {"id": login_link.user.id, "token": token}
        )

        return Response(data=token_serializer.data)


class WithdrawUser(APIView):
    """
    delete: 회원탈퇴

    - HTTP Header에 api-key Token 필요
        key: Authorization, value: Token [토큰값] (예시: Authorization: Token c5a4e25a7c5d8dc545c8d10740bfe655429c129b)
    """

    permission_classes = [permissions.IsAuthenticated]

    @method_decorator(
        name="delete",
        decorator=swagger_auto_schema(
            request_body=None,
            responses=None,
        ),
    )
    def delete(self, request):
        user = request.user

        try:
            token = Token.objects.get(user_id=user.id)
        except Token.DoesNotExist:
            pass

        login_link = get_login_link_data(request.user)
        with transaction.atomic():
            token.delete()
            login_link.link_id = None
            login_link.link_email = None
            login_link.save()
            user.phone = None
            user.nickname = None
            user.deleted_at = datetime.now()
            user.save()

        return Response(status=status.HTTP_200_OK)


class PasswordChange(APIView):
    """
    patch: 비밀번호 변경(Find Password & Change Password) API

    - type
        - 찾기 `"type":"find"`
        - 변경 `"type":"change"`

    - Change Password시
        - HTTP Header에 api-key Token 필요
            key: Authorization, value: Token [토큰값] (예시: Authorization: Token c5a4e25a7c5d8dc545c8d10740bfe655429c129b)

    """

    permission_classes = [permissions.AllowAny]

    @method_decorator(
        name="patch",
        decorator=swagger_auto_schema(
            request_body=PasswordChangeSerializer(), responses={200: ""}
        ),
    )
    def patch(self, request):
        ## TODO 추후 수정 필요 권한문제에 대해서
        serializer = get_serilaizer_check(PasswordChangeSerializer, request.data)

        type = serializer.data.get("type", None)
        email = serializer.data.get("email", None)
        password1 = serializer.data.get("password1", None)

        if type == "change":
            link = get_user_link_with_token(request.auth)
            email = link.link_email

        try:
            link = LoginLink.objects.get(
                link_email=email, type="E", user__deleted_at__isnull=True
            )
        except LoginLink.DoesNotExist:
            return UnprocessableEntityError(
                message=ugettext_lazy("User does not exists")
            )

        link.user.set_password(password1)
        link.user.save()

        return Response(status=status.HTTP_200_OK)


class SettingData(APIView):
    """
    get: 설정 데이터 조회

    - Setting 값 조회
    - HTTP Header에 api-key Token 필요
        key: Authorization, value: Token [토큰값]
        (예시: Authorization: Token c5a4e25a7c5d8dc545c8d10740bfe655429c129b)
    - device_type
        - 애플 `"device_type":"ios"`
        - 안드로이드 `"device_type":"aos"`
    """

    permission_classes = [permissions.IsAuthenticated]

    @method_decorator(
        name="get",
        decorator=swagger_auto_schema(
            request_body=None,
            responses={200: SettingDataResponseSerializer()},
        ),
    )
    def get(self, request):
        ## TODO 현재 구글 인증 사용 유무 판단하기 어려워 임시로 False 투입
        setting_serializer = SettingDataResponseSerializer(
            {
                "push_notifications": request.user.push_notification,
                "google_authenticator": False,
                "receive_promotional_email": request.user.agree_to_ad,
            }
        )

        return Response(status=status.HTTP_200_OK, data=setting_serializer.data)


class PushNotificationChange(APIView):
    """
    patch: 푸시 알림 수정 API

    - HTTP Header에 api-key Token 필요
        key: Authorization, value: Token [토큰값]
        (예시: Authorization: Token c5a4e25a7c5d8dc545c8d10740bfe655429c129b)

    """

    permission_classes = [permissions.IsAuthenticated]

    @method_decorator(
        name="patch",
        decorator=swagger_auto_schema(request_body=None, responses={200: ""}),
    )
    def patch(self, request):
        if request.user.push_notification:
            request.user.push_notification = False
        else:
            request.user.push_notification = True

        request.user.save()

        return Response(status=status.HTTP_200_OK)


class AdChange(APIView):
    """
    patch: 광고성 수신 동의 여부 수정 API

    - HTTP Header에 api-key Token 필요
        key: Authorization, value: Token [토큰값]
        (예시: Authorization: Token c5a4e25a7c5d8dc545c8d10740bfe655429c129b)

    """

    permission_classes = [permissions.IsAuthenticated]

    @method_decorator(
        name="patch",
        decorator=swagger_auto_schema(request_body=None, responses={200: ""}),
    )
    def patch(self, request):
        if request.user.agree_to_ad:
            request.user.agree_to_ad = False
        else:
            request.user.agree_to_ad = True

        request.user.save()

        return Response(status=status.HTTP_200_OK)


class PasswordConfirm(APIView):
    """
    post: 비밀번호 확인 API

    - HTTP Header에 api-key Token 필요
        key: Authorization, value: Token [토큰값]
        (예시: Authorization: Token c5a4e25a7c5d8dc545c8d10740bfe655429c129b)
    """

    permission_classes = [permissions.IsAuthenticated]

    @method_decorator(
        name="post",
        decorator=swagger_auto_schema(
            request_body=PasswordConfirmSerializer(), responses={200: ""}
        ),
    )
    def post(self, request):
        serializer = get_serilaizer_check(PasswordConfirmSerializer, request.data)

        custom_user = request.user
        password = serializer.data.get("password", None)

        if not password:
            return UnprocessableEntityError(
                message=ugettext_lazy("Password does not exists")
            )

        if custom_user.check_password(password):
            return Response(status=status.HTTP_200_OK)
        else:
            return UnprocessableEntityError(message=ugettext_lazy("Invalid password"))


class ProfileImageS3Upload(generics.CreateAPIView):
    """
    post: 프로필 이미지 S3 업로드 API

    - HTTP Header에 api-key Token 필요
        key: Authorization, value: Token [토큰값] (예시: Authorization: Token c5a4e25a7c5d8dc545c8d10740bfe655429c129b)
    - multipart/form-data 속성으로 image를 넘겨줘야함
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileImageS3UploadSerializer
    parser_classes = (MultiPartParser,)
    MAX_SIZE = 5242880  # 기본 제약은 5MB = 5 * 1024 * 1024 = 5242880

    def set_max_size(self, max_size):
        self.MAX_SIZE = max_size

    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        image = validated_data.get("image", None)
        if image is None:
            return UnprocessableEntityError(message="image does not exists")

        MAX_SIZE = self.MAX_SIZE
        max_size_str = filesizeformat(MAX_SIZE)
        if image.size >= MAX_SIZE:
            return UnprocessableEntityError(message=f"이미지의 크기가 {max_size_str}를 넘습니다.")

        serializer.save(user=self.request.user)


class ProfileimageChange(APIView):
    """
    patch: 사용자 프로필 이미지 변경 API

    - HTTP Header에 api-key Token 필요
        key: Authorization, value: Token [토큰값]
        (예시: Authorization: Token c5a4e25a7c5d8dc545c8d10740bfe655429c129b)

    """

    permission_classes = [permissions.IsAuthenticated]

    @method_decorator(
        name="patch",
        decorator=swagger_auto_schema(
            request_body=ProfileImageChangeSerializer(), responses={200: ""}
        ),
    )
    def patch(self, request):
        serializer = get_serilaizer_check(ProfileImageChangeSerializer, request.data)

        image = serializer.data.get("image", None)

        request.user.profile_image_url = image

        request.user.save()

        return Response(status=status.HTTP_200_OK)


class PhoneVerificaitonSend(APIView):
    """
    post: 핸드폰 번호 인증 발송 API

    - HTTP Header에 api-key Token 필요
        key: Authorization, value: Token [토큰값]
        (예시: Authorization: Token c5a4e25a7c5d8dc545c8d10740bfe655429c129b)

    - country_code_id
        - api문서 common -> 국가별 번호 코드 조회 확인하셔야합니다.

    - phone_number
        - `-`를 뺀 번호만 입력해주세요

    - dev환경에서는 인증번호가 `{"code":"111111111"}`형식으로 response 출력

    """

    permission_classes = [permissions.IsAuthenticated]

    @method_decorator(
        name="post",
        decorator=swagger_auto_schema(
            request_body=PhoneVerificationSendSerializer(), responses={200: ""}
        ),
    )
    def post(self, request):
        serializer = get_serilaizer_check(PhoneVerificationSendSerializer, request.data)

        country_code_id = serializer.data.get("country_code_id", None)
        phone_number = serializer.data.get("phone_number", None)

        country_code = CountryCode.objects.get(pk=country_code_id)

        total_phone_number = country_code.code + phone_number

        code = get_random_number_code(8)

        with transaction.atomic():
            PhoneVerification.objects.create(
                country_code=country_code,
                phone_number=phone_number,
                code=code,
                user=request.user,
            )
        if os.environ.get("ENVIRONMENT") == "production":
            aws_sms_single_send(
                total_phone_number, f"[project] Phone Verification Code\n{code}"
            )
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_200_OK, data={"code": f"{code}"})
        # 재전송 제한 시간 예시
        # resend_cooltime = datetime.now() - timedelta(seconds=30)
        # prev = PhoneVerification.objects.filter(
        #     phone_number=phone_number,
        #     created_at__gt=resend_cooltime,
        # ).order_by("-created_at").first()
        # if prev is None:
        #     PhoneVerification.objects.create(
        #         code=code,
        #         phone_number=phone_number,
        #     )
        #     return Response(status=status.HTTP_200_OK)
        # else:
        # return UnprocessableEntityError(
        #     message="wait 30 seconds",
        # )


class PhoneVerificaitonConfirm(APIView):
    """
    post: 핸드폰 번호 인증 확인 API

    - HTTP Header에 api-key Token 필요
        key: Authorization, value: Token [토큰값]
        (예시: Authorization: Token c5a4e25a7c5d8dc545c8d10740bfe655429c129b)

    - country_code_id
        - api문서 common -> 국가별 번호 코드 조회 확인하셔야합니다.
    - phone_number
        - `-`를 뺀 번호만 입력해주세요

    """

    permission_classes = [permissions.IsAuthenticated]

    @method_decorator(
        name="post",
        decorator=swagger_auto_schema(
            request_body=PhoneVerificationConfirmSerializer(),
            responses={200: ""},
        ),
    )
    def post(self, request):
        serializer = get_serilaizer_check(
            PhoneVerificationConfirmSerializer, request.data
        )

        today = datetime.now()

        country_code_id = serializer.data.get("country_code_id", None)
        phone_number = serializer.data.get("phone_number", None)
        code = serializer.data.get("code", None)

        try:
            phone_verification = PhoneVerification.objects.get(
                code=code,
                country_code_id=country_code_id,
                phone_number=phone_number,
                auth_check=False,
                created_at__year=today.year,
                created_at__month=today.month,
                created_at__day=today.day,
            )
        except PhoneVerification.DoesNotExist:
            return UnprocessableEntityError(message=ugettext_lazy("Incorrect Code"))

        recent_phone_verification = PhoneVerification.objects.filter(
            country_code_id=country_code_id,
            phone_number=phone_number,
            auth_check=False,
            created_at__year=today.year,
            created_at__month=today.month,
            created_at__day=today.day,
        ).order_by("-created_at")

        # 인증 제한 시간 10 분 예시
        intime = datetime.now() - timedelta(minutes=10)
        intime_obj = (
            PhoneVerification.objects.filter(
                country_code_id=country_code_id,
                phone_number=phone_number,
                created_at__gte=intime,
            )
            .order_by("-created_at")
            .first()
        )

        return verification_time_limit(
            request,
            intime_obj,
            phone_verification,
            recent_phone_verification,
            "phone",
        )
