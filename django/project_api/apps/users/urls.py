# users/urls.py
from users.views import (
    AdChange,
    EmailLogin,
    EmailLogout,
    EmailRegistration,
    EmailVerificationConfirm,
    EmailVerificationSend,
    LoginUserData,
    NicknameCheck,
    PasswordChange,
    PasswordConfirm,
    PhoneVerificaitonConfirm,
    PhoneVerificaitonSend,
    ProfileEdit,
    ProfileimageChange,
    ProfileImageS3Upload,
    PushNotificationChange,
    SettingData,
    SocialLogin,
    SocialRegistration,
    WithdrawUser,
)

from django.urls import path

urlpatterns = [
    path(
        "email/registration/",
        EmailRegistration.as_view(),
        name="email-registration",
    ),
    path(
        "email/verification/send/",
        EmailVerificationSend.as_view(),
        name="email-verification-send",
    ),
    path(
        "email/verification/confirm/",
        EmailVerificationConfirm.as_view(),
        name="email-verification-confirm",
    ),
    path(
        "email/login/",
        EmailLogin.as_view(),
        name="email-login",
    ),
    path(
        "email/logout/",
        EmailLogout.as_view(),
        name="email-logout",
    ),
    path(
        "nickname/check/",
        NicknameCheck.as_view(),
        name="nickname-check",
    ),
    path(
        "profile/",
        ProfileEdit.as_view(),
        name="profile-edit",
    ),
    path(
        "data/",
        LoginUserData.as_view(),
        name="login-user-data",
    ),
    path(
        "social/registration/",
        SocialRegistration.as_view(),
        name="social-registration",
    ),
    path(
        "social/login/",
        SocialLogin.as_view(),
        name="social-login",
    ),
    path(
        "withdraw/",
        WithdrawUser.as_view(),
        name="withdraw-user",
    ),
    path(
        "password/",
        PasswordChange.as_view(),
        name="password-change",
    ),
    path(
        "setting-data/",
        SettingData.as_view(),
        name="setting-data",
    ),
    path(
        "push-notification/",
        PushNotificationChange.as_view(),
        name="push-notification-change",
    ),
    path(
        "ad/",
        AdChange.as_view(),
        name="ad-change",
    ),
    path(
        "password/confirm/",
        PasswordConfirm.as_view(),
        name="password-confirm",
    ),
    path(
        "profile/upload-image/",
        ProfileImageS3Upload.as_view(),
        name="profile-upload",
    ),
    path(
        "profile/change-image/",
        ProfileimageChange.as_view(),
        name="profile-change",
    ),
    path(
        "phone/send/",
        PhoneVerificaitonSend.as_view(),
        name="phone-verification-send",
    ),
    path(
        "phone/confirm/",
        PhoneVerificaitonConfirm.as_view(),
        name="phone-verification-confirm",
    ),
]
