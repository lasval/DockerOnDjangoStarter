# project_api/utils.py (common utils)
# from django.core import mail
import base64
import random
import string
from collections import OrderedDict

import boto3
from botocore.exceptions import ClientError
from drf_yasg.inspectors import SwaggerAutoSchema
from drf_yasg.utils import no_body
from rest_framework import serializers, status
from rest_framework.exceptions import APIException
from rest_framework.response import Response


## TODO 클래스화 하기!
class StandardError(Response):
    def __init__(self, status_code: int, message: str, status):
        payload = {
            "status_code": status_code,
            "message": message,
            "details": {},
        }
        super().__init__(data=payload, status=status)


class BadRequestError(Response):
    def __init__(self, message: str):
        payload = {
            "status_code": 400,
            "message": message,
            "details": {},
        }
        super().__init__(data=payload, status=status.HTTP_400_BAD_REQUEST)


class UnprocessableEntityError(Response):
    def __init__(self, message: str):
        payload = {
            "status_code": 422,
            "message": message,
            "details": {},
        }
        super().__init__(data=payload, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class StandardException(APIException):
    detail = None
    status_code = None

    def __init__(self, status_code, message):
        StandardException.status_code = status_code
        StandardException.detail = message


# class DbDoesNotExist:
#     def


# class DbStandardErrorReponse():
#     def __init__(self):


# def dose(a, pk):
#     try:
#         a.objects.get(pk=1)
#     except a.DoesNotExist:
#         print("???")
#         pass


# ***************************************************************
# drf-yasg SWAGGER_SETTINGS에서 사용
# - read_only / write_only 필드가 doc에서 한번에 노출되지 않도록 하기 위함
# ***************************************************************
class ReadOnly:  # pragma: no cover
    def get_fields(self):
        new_fields = OrderedDict()
        for fieldName, field in super().get_fields().items():
            if not field.write_only:
                new_fields[fieldName] = field
        return new_fields


class BlankMeta:  # pragma: no cover
    pass


class WriteOnly:  # pragma: no cover
    def get_fields(self):
        new_fields = OrderedDict()
        for fieldName, field in super().get_fields().items():
            if not field.read_only:
                new_fields[fieldName] = field
        return new_fields


class ReadWriteAutoSchema(SwaggerAutoSchema):  # pragma: no cover
    def get_view_serializer(self):
        return self._convert_serializer(WriteOnly)

    def get_default_response_serializer(self):
        body_override = self._get_request_body_override()
        if body_override and body_override is not no_body:
            return body_override

        return self._convert_serializer(ReadOnly)

    def _convert_serializer(self, new_class):
        serializer = super().get_view_serializer()
        if not serializer:
            return serializer

        class CustomSerializer(new_class, serializer.__class__):
            class Meta(getattr(serializer.__class__, "Meta", BlankMeta)):
                ref_name = new_class.__name__ + serializer.__class__.__name__

        new_serializer = CustomSerializer(data=serializer.data)
        return new_serializer


def aws_email_single_send(recipient, subject, body_html):
    # Replace sender@example.com with your "From" address.
    # This address must be verified with Amazon SES.
    email = "info@popprika.com"
    name = "Corporation popprika"
    name_bytes = name.encode("utf8")
    name_base64 = base64.b64encode(name_bytes)
    name_base64_str = name_base64.decode("utf8")

    sender = "=?utf-8?B?" + name_base64_str + "?=" + " <{}>".format(email)

    SENDER = sender

    # Replace recipient@example.com with a "To" address. If your account
    # is still in the sandbox, this address must be verified.
    RECIPIENT = recipient

    # Specify a configuration set. If you do not want to use a configuration
    # set, comment the following variable, and the
    # ConfigurationSetName = CONFIGURATION_SET  argument below.
    # CONFIGURATION_SET = "ConfigSet"

    # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
    AWS_REGION = "ap-northeast-2"

    # The subject line for the email.
    SUBJECT = subject

    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = (
        "Amazon SES Test (Python)\r\n"
        "This email was sent with Amazon SES using the "
        "AWS SDK for Python (Boto)."
    )

    # The HTML body of the email.
    BODY_HTML = body_html

    CHARSET = "UTF-8"

    # 사용시에만 주석 풀것
    # Create a new SES resource and specify a region.
    ses_client = boto3.client("ses", region_name=AWS_REGION)
    response = ""
    # Try to send the email.
    try:
        # Provide the contents of the email.
        response = ses_client.send_email(
            Destination={
                "ToAddresses": [
                    RECIPIENT,
                ],
            },
            Message={
                "Body": {
                    "Html": {
                        "Charset": CHARSET,
                        "Data": BODY_HTML,
                    },
                    "Text": {
                        "Charset": CHARSET,
                        "Data": BODY_TEXT,
                    },
                },
                "Subject": {
                    "Charset": CHARSET,
                    "Data": SUBJECT,
                },
            },
            Source=SENDER,
            # If you are not using a configuration set, comment or delete the
            # following line
            # ConfigurationSetName="ConfigSet",
        )
        # Display an error if something goes wrong.
    except ClientError as e:
        print(e.response["Error"]["Message"])
    else:
        print("Email sent! Message ID:"),
        print(response["MessageId"])


def aws_sms_single_send(phone_number, messeage):
    sms_client = boto3.client(
        "sns",
        region_name="ap-northeast-1",
    )

    sms_client.set_sms_attributes(attributes={"DefaultSMSType": "Transactional"})

    sms_client.publish(
        PhoneNumber=phone_number,
        Message=messeage,
    )


def get_random_number_code(length: int):
    return "".join(random.choice(string.digits) for _ in range(length))


## TODO APIView 상속 받아서 새로운 APIView 만들어 사용해보기
def get_serilaizer_check(serilaizer: serializers, data):
    serializer = serilaizer(data=data)
    serializer.is_valid(raise_exception=True)

    return serializer
