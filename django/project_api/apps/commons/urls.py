from django.urls import path

from .views import (
    AppVersionView,
    CommonImageUploadView,
    CountryCodeView,
    TermsOfService,
)

urlpatterns = [
    path("upload-image/", CommonImageUploadView.as_view(), name="upload-image"),
    path("app-version/", AppVersionView.as_view(), name="app-version"),
    path("termsofservice/", TermsOfService.as_view(), name="termsofservice"),
    path("countrycode/", CountryCodeView.as_view(), name="countrycode"),
]
