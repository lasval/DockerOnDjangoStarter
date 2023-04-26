"""project_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from django.conf import settings
from django.contrib import admin
from django.urls import include, path

schema_view = get_schema_view(
    openapi.Info(
        title="project API",
        default_version="v0.1.0",
        description="""
        project API 문서 페이지 입니다.

        view를 생성/수정할 때, 주석영역을 적절하게 추가/수정하여 문서를 만들어주세요.
        """,
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="las@popprika.com"),
        license=openapi.License(name="BSD License"),
    ),
    validators=["flex"],
    public=True,
    permission_classes=(permissions.AllowAny,),
)

admin.site.site_title = "project ADMIN"
admin.site.site_header = "project ADMIN"
admin.site.site_url = None


urlpatterns = [
    # drf_yasg
    path(
        "swagger<str:format>",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(
        "redoc/",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
    # custom
    path("admin/", admin.site.urls),
    path("users/", include("users.urls")),
    path("commons/", include("commons.urls")),
    path("exercises/", include("exercises.urls")),
]
if settings.DEBUG:
    if settings.USING_TOOL == settings.SILK:
        urlpatterns += [path("silk/", include("silk.urls"))]

    if settings.USING_TOOL == settings.DDT:
        import debug_toolbar

        urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
