from conftest import (
    DEFAULT_EMAIL_LINK_DATA,
    DEFAULT_EMAIL_LOGIN_DATA,
    DEFAULT_EMAIL_USER_DATA,
    unauthorized_after_login,
)
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import EmailVerification, LoginLink, PhoneVerification, User

from django.urls import reverse


class UsersTest(APITestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_user_profile(self):
        """force_authenticate가 동작하는지 테스트"""

        user = User.objects.all().first()
        self.client.force_authenticate(user=user)
        url = reverse("login-user-data")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    ## TODO 정상적인 케이스말고 예외처리가 잘되어있는지에 대한 4xx 처리도 필요하다.
    def test_email_registration(self):
        """이메일 회원가입 로직 테스트"""

        email_send_url = reverse("email-verification-send")
        email_send_req_body = {
            "type": "sign_upaa",
            "email": "las@popprika.com",
        }
        response = self.client.post(email_send_url, email_send_req_body, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        email_send_req_body["type"] = "sign_up"
        response = self.client.post(email_send_url, email_send_req_body, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        email_verification = EmailVerification.objects.all().first()
        email_confirm_url = reverse("email-verification-confirm")
        email_confirm_req_body = {
            "type": "sign_upp",
            "email": "las@popprika.com",
            "code": email_verification.code,
        }
        response = self.client.post(
            email_confirm_url, email_confirm_req_body, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        email_confirm_req_body["type"] = "sign_up"
        response = self.client.post(
            email_confirm_url, email_confirm_req_body, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        email_registration_url = reverse("email-registration")
        email_registration_req_body = {
            "email": "las@popprika.com",
            "password1": "qwerty12",
            "password2": "qwerty12",
            "device_type": "ioss",
            "agree_to_ad": True,
        }
        response = self.client.post(
            email_registration_url, email_registration_req_body, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        email_registration_req_body["device_type"] = "ios"

        response = self.client.post(
            email_registration_url, email_registration_req_body, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        email_registration_req_body["password1"] = "qwerty12!"

        response = self.client.post(
            email_registration_url, email_registration_req_body, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        email_registration_req_body["password2"] = "qwerty12!"

        response = self.client.post(
            email_registration_url, email_registration_req_body, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        users = LoginLink.objects.filter(
            link_email="las@popprika.com", user__deleted_at__isnull=True
        )
        if users.exists:
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_email_login(self):
        """이메일 로그인 테스트"""

        login_url = reverse("email-login")
        login_req_body = {
            "email": DEFAULT_EMAIL_LINK_DATA["link_email"],
            "password": "qweertqweqweqw",
        }
        response = self.client.post(login_url, login_req_body, format="json")
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

        login_req_body["password"] = DEFAULT_EMAIL_USER_DATA["password"]
        response = self.client.post(login_url, login_req_body, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout(self):
        """로그아웃 테스트"""

        logout_url = reverse("email-logout")
        response = self.client.post(logout_url)
        unauthorized_after_login(self, response)

        response = self.client.post(logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=None)

    def test_profile_edit(self):
        """프로필 수정 테스트"""

        profile_edit_url = reverse("profile-edit")
        profile_edit_req_body = {
            "nickname": "las",
            "gender": "S",
            "height": "176",
            "weight": "80",
            "birthdate": "1993-06-01",
        }
        response = self.client.patch(
            profile_edit_url, profile_edit_req_body, format="json"
        )
        unauthorized_after_login(self, response)

        response = self.client.patch(
            profile_edit_url, profile_edit_req_body, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        profile_edit_req_body["gender"] = "M"
        response = self.client.patch(
            profile_edit_url, profile_edit_req_body, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=None)

    def test_get_user_date(self):
        """유저 프로필 조회 테스트"""

        user_data_url = reverse("login-user-data")
        response = self.client.get(user_data_url)
        unauthorized_after_login(self, response)

        response = self.client.get(user_data_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=None)

    def test_withdraw(self):
        """유저 회원탈퇴 테스트"""

        withdraw_url = reverse("withdraw-user")
        response = self.client.delete(withdraw_url)
        unauthorized_after_login(self, response)

        response = self.client.delete(withdraw_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            LoginLink.objects.filter(
                link_email=DEFAULT_EMAIL_LOGIN_DATA["email"],
                type=DEFAULT_EMAIL_LINK_DATA["type"],
                user__deleted_at__isnull=True,
            ).exists(),
            False,
        )
        self.client.credentials(HTTP_AUTHORIZATION=None)

    def test_password_change(self):
        """유저 비밀번호 변경 테스트"""

        password_change_url = reverse("password-change")
        password_change_req_body = {
            "type": "find",
            "email": DEFAULT_EMAIL_LOGIN_DATA["email"],
            "password1": "qwerty12!",
            "password2": "qwerty12!",
        }
        response = self.client.patch(
            password_change_url, password_change_req_body, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_setting_data(self):
        """셋팅값 조회 테스트"""

        setting_data_url = reverse("setting-data")
        response = self.client.get(setting_data_url)
        unauthorized_after_login(self, response)

        response = self.client.get(setting_data_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_push_data_edit(self):
        """푸시 알림 수정 테스트"""

        push_data_edit_url = reverse("push-notification-change")
        response = self.client.patch(push_data_edit_url)
        unauthorized_after_login(self, response)

        response = self.client.patch(push_data_edit_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_ad_data_edit(self):
        """광고 수신 동의 수정 테스트"""

        ad_data_edit_url = reverse("ad-change")
        response = self.client.patch(ad_data_edit_url)
        unauthorized_after_login(self, response)

        response = self.client.patch(ad_data_edit_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_confirm(self):
        """비밀번호 확인 테스트"""

        password_confirm_url = reverse("password-confirm")
        password_confirm_req_body = {"password": DEFAULT_EMAIL_LOGIN_DATA["password"]}
        response = self.client.post(
            password_confirm_url, password_confirm_req_body, format="json"
        )
        unauthorized_after_login(self, response)

        response = self.client.post(
            password_confirm_url, password_confirm_req_body, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_phone_verification(self):
        """핸드폰 번호 인증 테스트"""

        phone_verification_send_url = reverse("phone-verification-send")
        phone_verification_send_req_body = {
            "country_code_id": 1,
            "phone_number": "01051742021",
        }
        response = self.client.post(
            phone_verification_send_url,
            phone_verification_send_req_body,
            format="json",
        )
        unauthorized_after_login(self, response)

        response = self.client.post(
            phone_verification_send_url,
            phone_verification_send_req_body,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        phone_verification = PhoneVerification.objects.all().first()

        phone_verification_confirm_url = reverse("phone-verification-send")
        phone_verification_confirm_req_body = {
            "country_code_id": 1,
            "phone_number": "01051742021",
            "code": phone_verification.code,
        }

        response = self.client.post(
            phone_verification_confirm_url,
            phone_verification_confirm_req_body,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
