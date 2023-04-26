from project_api.custom_http_status import HTTPStatus
from project_api.utils import StandardError, StandardException
from rest_framework.views import exception_handler

from django.utils.translation import ugettext_lazy


def custom_exception_handler(exc, context):
    """Custom API exception handler."""
    # print(exc, context)
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if response is not None:
        # Using the description's of the HTTPStatus class as error message.
        http_code_to_message = {v.value: v.description for v in HTTPStatus}

        error_payload = {
            "status_code": 0,
            "message": "",
        }
        error = error_payload
        status_code = response.status_code

        error["status_code"] = status_code

        if type(exc) == StandardException or type(exc) == StandardError:
            error["message"] = str(exc)
            error["details"] = {}
        else:
            try:
                error["message"] = f"{http_code_to_message[status_code]} [Parameter: "
                field_name_list = []
                for field_name, field_error in response.data.items():
                    field_name_list.append(field_name)
                error["message"] += ",".join(field_name_list)
                error["message"] += "]"
                error["details"] = response.data
            except KeyError:
                error["message"] = ugettext_lazy("error")

        if error_payload["status_code"] == 401:
            error_payload["message"] = "존재하지 않는 토큰입니다. 다시 로그인 해주십시오"

        response.data = error_payload
    return response
