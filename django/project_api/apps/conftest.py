from datetime import datetime

import pytest
from commons.models import CountryCode
from rest_framework import status
from users.models import DeviceType, Gender, LoginLink, LoginType, User

DEFAULT_EMAIL_USER_DATA = {
    "user_code": "EMAIL_USERCODE",
    "nickname": "이메일유저",
    "device_type": DeviceType.AOS.value,
    "gender": Gender.MALE.value,
    "height": 175,
    "weight": 80,
    "birthdate": datetime.now(),
    "agree_to_ad": True,
    "push_notification": False,
    "password": "qwerty12!",
    "country_code_id": 1,
}

DEFAULT_GOOGLE_USER_DATA = {
    "user_code": "GOOGLE_USERCODE",
    "nickname": "구글유저",
    "device_type": DeviceType.AOS.value,
    "gender": Gender.FEMALE.value,
    "height": 155,
    "weight": 45,
    "birthdate": datetime.now(),
    "agree_to_ad": False,
    "push_notification": False,
    "password": "qwerty12!",
    "country_code_id": 2,
}

DEFAULT_APPLE_USER_DATA = {
    "user_code": "APPLE_USERCODE",
    "nickname": "애플유저",
    "device_type": DeviceType.IOS.value,
    "gender": Gender.MALE.value,
    "height": 175,
    "weight": 80,
    "birthdate": datetime.now(),
    "agree_to_ad": True,
    "push_notification": True,
    "password": "qwerty12!",
    "country_code_id": 3,
}


DEFAULT_EMAIL_LINK_DATA = {
    "type": LoginType.EMAIL.value,
    "link_id": None,
    "link_email": "xxx@google.com",
}

DEFAULT_GOOGLE_LINK_DATA = {
    "type": LoginType.GOOGLE.value,
    "link_id": "123184728947189273",
    "link_email": "xxx@google.com",
}

DEFAULT_APPLE_LINK_DATA = {
    "type": LoginType.APPLE.value,
    "link_id": "1283912739012839081",
    "link_email": "xxx@google.com",
}

DEFAULT_EMAIL_LOGIN_DATA = {
    "email": "xxx@google.com",
    "password": "qwerty12!",
}


def create_default_data():
    country_code_list = [
        ["Republic of korea", "한국", "+82"],
        ["United States", "미국", "+1"],
        ["Canada", "캐나다", "+1"],
        ["Egypt", "이집트", "+20"],
        ["Republic of Ghana", "가나", "+233"],
        ["Nigeria", "나이지리아", "+234"],
        ["Kenya", "케냐", "+254"],
        ["Republic of South Africa", "남아프리카 공화국", "+27"],
        ["Greece", "그리스", "+30"],
        ["Netherlands", "네덜란드", "+31"],
        ["Belguim", "벨기에", "+32"],
        ["France", "프랑스", "+33"],
        ["Spain", "스페인", "+34"],
        ["Portugal", "포르투갈", "+351"],
        ["Iceland", "아이슬란드", "+354"],
        ["Hungary", "헝가리", "+36"],
        ["Ukraine", "우크라이나", "+380"],
        ["Italy", "이탈리아", "+39"],
        ["Swiss", "스위스", "+41"],
        ["UK", "영국", "+44"],
        ["Denmark", "덴마크", "+45"],
        ["Sweden", "스웨덴", "+46"],
        ["Norway", "노르웨이", "+47"],
        ["Poland", "폴란드", "+48"],
        ["Germany", "독일", "+49"],
        ["Nicaragua", "니카라과", "+505"],
        ["Mexico", "멕시코", "+52"],
        ["Argentina", "아르헨티나", "+54"],
        ["Brazil", "브라질", "+55"],
        ["Chlie", "칠레", "+56"],
        ["Venezuela", "베네수엘라", "+58"],
        ["Uruguay", "우루과이", "+598"],
        ["Malaysia", "말레이시아", "+60"],
        ["Australia", "오스트레일리아", "+61"],
        ["Indonesia", "인도네시아", "+62"],
        ["Philippine", "필리핀", "+63"],
        ["New Zealand", "뉴질랜드", "+64"],
        ["Singapore", "싱가포르", "+65"],
        ["Thailand", "태국", "+66"],
        ["Russia", "러시아", "+7"],
        ["Japan", "일본", "+81"],
        ["Vietnam", "베트남", "+84"],
        ["Hongkong", "홍콩", "+852"],
        ["China", "중국", "+86"],
        ["Bangladesh", "방글라데시", "+880"],
        ["Taiwan", "대만", "+886"],
        ["Turkey", "튀르키예", "+90"],
        ["India", "인도", "+91"],
        ["Iraq", "이라크", "+964"],
        ["Saudi Arabia", "사우디 아라비아", "+966"],
        ["United Arab Emirates", "아랍 에미리트", "+971"],
        ["Israel", "이스라엘", "+972"],
        ["Nepal", "네팔", "+977"],
        ["Iran", "이란", "+98"],
    ]

    country_codes = [
        CountryCode(country_en_name=data[0], country_ko_name=data[1], code=[2])
        for data in country_code_list
    ]

    CountryCode.objects.bulk_create(country_codes)

    email_user = User.objects.create(
        user_code=DEFAULT_EMAIL_USER_DATA["user_code"],
        nickname=DEFAULT_EMAIL_USER_DATA["nickname"],
        device_type=DEFAULT_EMAIL_USER_DATA["device_type"],
        gender=DEFAULT_EMAIL_USER_DATA["gender"],
        height=DEFAULT_EMAIL_USER_DATA["height"],
        weight=DEFAULT_EMAIL_USER_DATA["weight"],
        birthdate=DEFAULT_EMAIL_USER_DATA["birthdate"],
        agree_to_ad=DEFAULT_EMAIL_USER_DATA["agree_to_ad"],
        push_notification=DEFAULT_EMAIL_USER_DATA["push_notification"],
        country_code_id=DEFAULT_EMAIL_USER_DATA["country_code_id"],
    )

    google_user = User.objects.create(
        user_code=DEFAULT_GOOGLE_USER_DATA["user_code"],
        nickname=DEFAULT_GOOGLE_USER_DATA["nickname"],
        device_type=DEFAULT_GOOGLE_USER_DATA["device_type"],
        gender=DEFAULT_GOOGLE_USER_DATA["gender"],
        height=DEFAULT_GOOGLE_USER_DATA["height"],
        weight=DEFAULT_GOOGLE_USER_DATA["weight"],
        birthdate=DEFAULT_GOOGLE_USER_DATA["birthdate"],
        agree_to_ad=DEFAULT_GOOGLE_USER_DATA["agree_to_ad"],
        push_notification=DEFAULT_GOOGLE_USER_DATA["push_notification"],
        country_code_id=DEFAULT_GOOGLE_USER_DATA["country_code_id"],
    )

    apple_user = User.objects.create(
        user_code=DEFAULT_APPLE_USER_DATA["user_code"],
        nickname=DEFAULT_APPLE_USER_DATA["nickname"],
        device_type=DEFAULT_APPLE_USER_DATA["device_type"],
        gender=DEFAULT_APPLE_USER_DATA["gender"],
        height=DEFAULT_APPLE_USER_DATA["height"],
        weight=DEFAULT_APPLE_USER_DATA["weight"],
        birthdate=DEFAULT_APPLE_USER_DATA["birthdate"],
        agree_to_ad=DEFAULT_APPLE_USER_DATA["agree_to_ad"],
        push_notification=DEFAULT_APPLE_USER_DATA["push_notification"],
        country_code_id=DEFAULT_APPLE_USER_DATA["country_code_id"],
    )

    email_user.set_password(DEFAULT_EMAIL_USER_DATA["password"])
    google_user.set_password(DEFAULT_GOOGLE_USER_DATA["password"])
    apple_user.set_password(DEFAULT_APPLE_USER_DATA["password"])

    email_user.save()
    google_user.save()
    apple_user.save()

    links = [
        LoginLink(
            type=DEFAULT_EMAIL_LINK_DATA["type"],
            link_id=DEFAULT_EMAIL_LINK_DATA["link_id"],
            link_email=DEFAULT_EMAIL_LINK_DATA["link_email"],
            user_id=email_user.id,
        ),
        LoginLink(
            type=DEFAULT_GOOGLE_LINK_DATA["type"],
            link_id=DEFAULT_GOOGLE_LINK_DATA["link_id"],
            link_email=DEFAULT_GOOGLE_LINK_DATA["link_email"],
            user_id=google_user.id,
        ),
        LoginLink(
            type=DEFAULT_APPLE_LINK_DATA["type"],
            link_id=DEFAULT_APPLE_LINK_DATA["link_id"],
            link_email=DEFAULT_APPLE_LINK_DATA["link_email"],
            user_id=apple_user.id,
        ),
    ]

    LoginLink.objects.bulk_create(links)


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        create_default_data()


def login_process(api_client, user_data):
    login_url = "/users/email/login/"
    response = api_client.post(login_url, user_data)
    token = response.data["token"]
    api_client.credentials(HTTP_AUTHORIZATION="Token " + token)


def unauthorized_after_login(test_self, response):
    test_self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    login_process(test_self.client, DEFAULT_EMAIL_LOGIN_DATA)
