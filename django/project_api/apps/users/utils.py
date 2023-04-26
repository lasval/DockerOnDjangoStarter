# users/utils.py
import os
import uuid
from typing import Final, Optional

from project_api.utils import StandardError, StandardException
from google.auth.transport import requests as google_auth_requests
from google.oauth2 import id_token as google_auth_id_token
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from users.models import LoginLink

from django.contrib.auth.password_validation import (
    CommonPasswordValidator,
    MinimumLengthValidator,
    NumericPasswordValidator,
)
from django.core.validators import validate_email as django_validate_email
from django.utils.translation import ugettext_lazy


class ValidationErrorStrs:
    """
    validation에서 사용하는 문구 모음 (static하게 사용하기 위함)
    - django에 설정된 에러문구를 그대로 사용할 수도 있지만,
      언어에 따른 처리를 직접 해주기 위해 해당 문구를 사용하는 방식으로 처리
    """

    pw_required: Final = "비밀번호를 입력해 주세요."
    pw_not_match: Final = "비밀번호가 일치하지 않습니다."
    pw_min_length: Final = "비밀번호가 너무 짧습니다. 최소 8 문자를 포함해야 합니다."
    pw_common: Final = "비밀번호가 너무 일상적인 단어입니다."
    pw_numeric: Final = "비밀번호가 전부 숫자로 되어 있습니다."
    email_required: Final = "이메일을 입력해 주세요."
    email_not_valid: Final = "유효한 이메일 주소를 입력하십시오."
    email_exist: Final = "이미 가입한 이메일입니다."
    user_type_required: Final = "유저타입이 필요합니다."
    user_type_not_valid: Final = "올바르지 않은 유저타입 입니다."
    user_auth_failed: Final = "이메일 또는 비밀번호가 일치하지 않습니다."


class RegistrationValidationValues:
    def __init__(self, request):
        self.email = request.data.get("email")
        self.password1 = request.data.get("password1")
        self.password2 = request.data.get("password2")


class LoginValidationValues:
    def __init__(self, request):
        self.email = request.data.get("email")
        self.password = request.data.get("password")


def validate_password_equality(
    password1: str, password2: str
) -> Optional[StandardError]:
    if password1 != password2:
        return StandardError(
            status_code=422,
            message=ValidationErrorStrs.pw_not_match,
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    return None


def validate_password_format(password: str) -> Optional[StandardError]:
    """
    django validator들을 그대로 현상황에선 언어를 상황에 맞게 컨트롤 할 수가 없다고 판단하여
    번거럽더라도 각각 try-except구문으로 구분하여 직접 정의 한 에러문구와 함께 처리
    (한번에 처리하면 어떤 에러인지 알 수 없으므로)
    추후, 더 좋은 방법이 생기면 그것으로 변경할 것
    """
    validate_error_strs = []
    try:
        MinimumLengthValidator().validate(password)
    except Exception:
        validate_error_strs.append(ValidationErrorStrs.pw_min_length)

    try:
        CommonPasswordValidator().validate(password)
    except Exception:
        validate_error_strs.append(ValidationErrorStrs.pw_common)

    try:
        NumericPasswordValidator().validate(password)
    except Exception:
        validate_error_strs.append(ValidationErrorStrs.pw_numeric)

    if len(validate_error_strs) > 0:
        return StandardError(
            status_code=400,
            message=validate_error_strs,
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    return None


def validate_email(email: str) -> Optional[StandardError]:
    try:
        django_validate_email(email)
    except Exception:
        return StandardError(
            status_code=422,
            message=ValidationErrorStrs.email_not_valid,
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    return None


def validate_registration(
    value_obj: RegistrationValidationValues,
) -> Optional[StandardError]:
    # 필수항목 미입력 체크
    insufficient_params = []
    if value_obj.email is None:
        insufficient_params.append(ValidationErrorStrs.email_required)
    if value_obj.password1 is None or value_obj.password2 is None:
        insufficient_params.append(ValidationErrorStrs.pw_required)
    if len(insufficient_params) > 0:
        return StandardError(
            status_code=400,
            message=insufficient_params,
            status=status.HTTP_400_BAD_REQUEST,
        )

    # 이메일 형식 체크
    email_validation_result = validate_email(value_obj.email)
    if isinstance(email_validation_result, StandardError):
        return email_validation_result

    # 비밀번호 일치 체크
    password_equality_validation_result = validate_password_equality(
        value_obj.password1, value_obj.password2
    )
    if isinstance(password_equality_validation_result, StandardError):
        return password_equality_validation_result

    # 비밀번호 최소 길이 / 복잡성(너무 일상적인지 & 숫자로만 되어있는지) 체크
    password_format_validation_result = validate_password_format(value_obj.password1)
    if isinstance(password_format_validation_result, StandardError):
        return password_format_validation_result

    # 모든 체크를 통과하면 None을 리턴
    return None


def returnUserAuthFailedError() -> StandardError:
    return StandardError(
        status_code=401,
        message=ValidationErrorStrs.user_auth_failed,
        status=status.HTTP_401_UNAUTHORIZED,
    )


def validate_login(
    value_obj: LoginValidationValues,
) -> Optional[StandardError]:
    # 필수항목 미입력 체크
    insufficient_params = []
    if value_obj.email is None:
        insufficient_params.append(ValidationErrorStrs.email_required)
    if value_obj.password is None:
        insufficient_params.append(ValidationErrorStrs.pw_required)
    if len(insufficient_params) > 0:
        return StandardError(
            status_code=400,
            message=insufficient_params,
            status=status.HTTP_400_BAD_REQUEST,
        )

    # 위의 모든 체크를 통과했다면 None을 리턴
    return None


def is_user_code_exist(user_code):
    """
    user code가 이미 존재하는지 체크하는 함수
    """
    from .models import User

    users = User.objects.filter(user_code=user_code)
    if users.exists():
        return True
    else:
        return False


def generate_user_code():
    """
    uuid를 이용해서 unique한 user code를 생성하는 함수
    유저 초기 생성(createsuperuser 등)에서는 UserModel을 추가할 수 없기 떄문에
    DB단의 중복체크 없이 생성한다.
    """
    uuid_str = uuid.uuid4().hex[:6].upper()
    return uuid_str


def generate_unique_user_code():
    """
    uuid를 이용해서 unique한 user code를 생성하는 함수
    uuid로 동일한 값이 나왔을 경우 (collision) 새로운 uuid를 구하여
    uuid값을 새로 만든다.

    해당 코드는 uuid에서 앞의 6자리를 가져다 쓰기 때문에
    경우의 수에 따라 최대 1600만건 정도까지 커버 가능
    그 이상이 되는 경우에는 다른 처리 필요
    """
    user_code = generate_user_code()

    if is_user_code_exist(user_code) is True:
        return generate_unique_user_code()
    else:
        return user_code


def google_auth(id_token, google_id):
    """
    google api 활용하여 받아온 token과 request_google_id를 비교하여 한번더 유효성 검사 진행
    """

    GOOGLE_WEB_CLIENT_ID = os.environ.get("GOOGLE_WEB_CLIENT_ID")

    ## TODO id_token third_party 명 바꾸든 아니면 내 token값 변경하여 사용하기
    ## requests도 좀 더 명확하게 명명하기
    try:
        google_id_info = google_auth_id_token.verify_oauth2_token(
            id_token, google_auth_requests.Request(), GOOGLE_WEB_CLIENT_ID
        )

        google_id_from_oauth = google_id_info["sub"]
    except Exception as e:
        if e == ValueError:
            raise StandardException(
                422,
                ugettext_lazy("id_token is invalid"),
            )
        else:
            raise StandardException(
                422,
                str(e),
            )

    if google_id_from_oauth != google_id:
        raise StandardException(
            422,
            ugettext_lazy("google_id does not match"),
        )


def get_user_link_with_token(token):
    try:
        token = Token.objects.get(key=token)
    except Token.DoesNotExist:
        raise StandardException(
            422,
            message=ugettext_lazy("uid dose not exists"),
        )

    try:
        link = LoginLink.objects.get(
            user_id=token.user.id, user__deleted_at__isnull=True
        )
    except Token.DoesNotExist:
        raise StandardException(
            422,
            message=ugettext_lazy("uid dose not exists"),
        )

    return link


def get_login_link_data(user):
    try:
        login_link = LoginLink.objects.get(user=user, user__deleted_at__isnull=True)
    except LoginLink.DoesNotExist:
        raise StandardException(
            422,
            ugettext_lazy("User does not exists"),
        )

    return login_link


def verification_time_limit(
    request,
    intime_obj,
    verification,
    recent_verification,
    verification_type=None,
):
    if intime_obj is not None and intime_obj.code == verification.code:
        if recent_verification.exists():
            if recent_verification[0] != verification:
                raise StandardException(
                    422,
                    ugettext_lazy("Incorrect Code"),
                )
            else:
                verification.auth_check = True
                verification.save()
        print(verification_type)
        if verification_type == "phone":
            print(verification.phone_number)
            request.user.phone = verification.phone_number
            request.user.save()
        return Response(status=status.HTTP_200_OK)
    else:
        raise StandardException(
            422,
            message=ugettext_lazy("Time expried"),
        )
