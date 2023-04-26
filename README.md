# Quick summary

# 기술 스택

| Python | Postgresql | Nginx | Docker |
| :----: | :--------: | :---: | :----: |
| ![py]  |   ![po]    | ![ng] | ![do]  |

# 사용중인 AWS 서비스

|  EC2  |  S3   | CloudFront | Route53 |  SES  |  SNS  |  ECR  |
| :---: | :---: | :--------: | :-----: | :---: | :---: | :---: |
| ![ec] | ![s3] |   ![cf]    |  ![rt]  | ![se] | ![sn] | ![ER] |

# 기본 디렉토리 구조 및 설명

Docker Compose를 이용하여 한번에 django 컨테이너와 nginx 컨테이너를 실행하고 연결시켜주기 위해
아래와 같은 구조로 디렉토리를 구성함

**기본 디렉토리 구조 (숨김파일 제외)**

```bash
├── django
├── nginx
├── README.md
├── docker-compose-dev.yml
├── docker-compose-local.yml
└── docker-compose.yml
```

**기본 디렉토리 구조 (숨김파일 포함)**

```bash
├── .git
├── django
├── nginx
├── .env.dev
├── .env.prod
├── .gitignore
├── README.md
├── docker-compose-dev.yml
├── docker-compose-local.yml
└── docker-compose.yml
```

**각 디렉토리 및 파일 설명**

- .git: 깃 디렉토리
- django: Django 프로젝트가 담긴 디렉토리
  (Dockerize를 위해 해당 디렉토리 내부에 `Dockerfile`과 `requirements.txt`를 추가함)
- nginx: Production모드로 django 프로젝트 컨테이너를 실행할 때 사용하는 nginx 관련 디렉토리
  (Dockerize를 위한 nginx `Dockerfile`과 nginx 설정파일인 `nginx.conf`가 포함된 디렉토리)
- .env.dev: Dev 모드로 빌드/실행할 때 참조하는 env파일 (Django내에서 사용하는 설정 값)
- .env.prod: Production 모드로 빌드/실행할 때 참조하는 env파일 (Django내에서 사용하는 설정 값)
- .gitignore: gitignore파일 (django/nginx 디렉토리 상위에 있기 때문에 django관련 파일을 무시하기 위해 /django/static과 같이 표현해줌)
- README.md: git 저장소 (bitbucket)에서 보여지는 README markdown 파일
  (프로젝트 관련 설명 포함)
- docker-compose-dev.yml: Dev 모드로 빌드/실행할 때 사용하는 `docker-compose`파일
  - 실행 예시: $ docker-compose -f docker-compose-dev.yml up —build
- docker-compose-local.yml: local에서 빌드/실행할 때 사용하는 `docker-compose`파일
  - 실행 예시: $ docker-compose -f docker-compose-local.yml up —build
- docker-compose.yml: Production 모드로 빌드/실행할 때 사용하는 `docker-compose`파일
  - 실행 예시: $ docker-compose up -d —build
  - docker-compose.yml은 docker-compose기본 파일이므로 따로 명령어에서 지정해주지 않아도 됨

# 실행/개발 전 사전 준비사항

Docker 관련 설치 가이드들은 Notion에서 확인하실 수 있습니다.

[Notion 개발 설치 가이드 모음](https://www.notion.so/gymt/Docker-9f4556b325bc4abea2f8b51f402fb4bd)

docker compose 설치 관련 문제가 생기면 도커 공식 홈페이지 참조

[https://docs.docker.com/compose/install/](https://docs.docker.com/compose/install/)

## **4. 필요한 환경변수 파일 생성 및 저장(.env.prod & .env.dev & /django/.env)**

.env.prod: Docker Compose를 사용할 때 Production 모드의 환경변수로 사용할 파일

```bash
DEBUG=0
SECRET_KEY=시크릿키입력
DJANGO_ALLOWED_HOSTS=Django에서 Allow Host로 사용할 값들 (띄어쓰기로 구분하여 작성, ex: 11.11.11.11 localhost [::1])
DB_ENGINE=django.db.backends.postgresql (postgreSQL 사용 예시)
DB_NAME=Production용 DB명
DB_USER=Production용 DB에 접속할 유저명
DB_PASSWORD=Production용 DB에 접속할 유저의 비밀번호
DB_HOST=Production용 DB Host주소
DB_PORT=Production용 DB 포트
```

.env.dev: Docker Compose를 사용할 때 Dev 모드의 환경변수로 사용할 파일
/django/.env: docker를 사용하지 않고 pipenv환경내에서 runserver로 실행할 때 필요한 파일 (.env.dev파일과 동일)

```bash
DEBUG=1
SECRET_KEY=시크릿키입력 ## ex)
DJANGO_ALLOWED_HOSTS=* (Dev 모드에서는 모두 허용해주기 위해 *를 지정)
DB_ENGINE=django.db.backends.postgresql (postgreSQL 사용 예시)
DB_NAME=QA or DEV용 DB명 ## ex) test_db
DB_USER=QA or DEV용 DB에 접속할 유저명 ## ex) test_db_admin
DB_PASSWORD=QA or DEV용 DB에 접속할 유저의 비밀번호 ## ex) admin_password
DB_HOST=QA or DEV용 DB Host주소 ## ex) db.devdb.com
DB_PORT=QA or DEV용 DB 포트 ## ex) 5432
```

---

# **Docker 명령어를 이용한 실행**

## **Production 모드로 이미지 생성 및 실행:**

Production 모드는 소스코드와 static 파일들을 컨테이너에 복사하고 독립적으로 실행한다.

따라서, 실행전 필요하다면 아래 명령어들을 선행적으로 실행해주어야 해당 사항이 반영된다.

(참고로 django 관련 명령어는 pipenv등의 로컬의 가상환경내에서 실행하는 것을 권장한다. 아래 쉘 명령어 입력 예시에서 앞의 (django)부분은 pipenv 가상환경임을 의미)

(Docker Compose 빌드/실행 이전에) `makemigrations`과 `migrate` 명령어는 필요시에 실행한다.

```bash
(django) $ python manage.py makemigrations
```

```bash
(django) $ python manage.py migrate
```

Producntion 모드로 빌드/실행하기 전에 `collectstatic`은 필수로 실행해주는 것을 권장한다.

```bash
(django) $ python manage.py collectstaticn
```

프로젝트 root 디렉토리에서 아래 명령어를 실행

```bash
$ docker-compose up -d --build
```

명령어 관련 설명

- `up`: Docker Compose(`docker-compose.yml` 파일)에 정의된 모든 서비스 컨테이너들을 한 번에 생성하고 실행하기 위한 명령어. 단, 해당 명령어에 `--build` 옵션을 명시해주지 않으면 변경사항이 반영되지 않음
- `-d` 옵션: detached 모드로써 백그라운드로 실행하여 로그가 보이지 않도록 함
- `--build`: 명시적으로 이미지를 새로 빌드하는 옵션. 프로젝트 코드에 변경사항이 있을 경우 해당 옵션을 명시해줘야만 반영됨

## **Dev 모드로 이미지 생성 및 실행:**

프로젝트 root 디렉토리에서 아래 명령어를 실행

```bash
$ docker-compose -f docker-compose-dev.yml up --build
```

명령어 관련 설명

- `up`: Production 모드와 동일
- `--build`: Production 모드와 동일
- `-f`: docker-compose-dev.yml파일을 통해 빌드/실행하기 위한 옵션 (해당 옵션을 지정하지 않으면 docker-compose.yml파일을 참조하여 빌드/실행됨)
- 참고사항(1): Dev 모드로써 서버 로그를 실시간으로 확인하기 위해서 -d 옵션은 주지 않음
- 참고사항(2): Dev 모드에서는 코드 변경을 실시간으로 반영하기 위해 django 디렉토리 하위의 `Dockerfile.dev`파일에 정의된 값들을 통해 로컬의 소스코드를 컨테이너와 바인딩 시킴

### **Production or Dev 모드로 빌드/실행할 때 주의해야할 점**

`--build` 옵션을 통해 Production 모드나 Dev 모드로 컨테이너를 실행할 때 코드 상에 변경사항이 있으면 새로운 이미지가 만들어지게 된다.

코드 변경 전 이미지

```bash
$ docker images
REPOSITORY           TAG            IMAGE ID       CREATED         SIZE
project/django       latest         bcd85ffe3187   8 minutes ago   647MB
project/django-dev   latest         7121aaf87ebe   3 hours ago     994MB
project/nginx        latest         ba7b66ec5f59   22 hours ago    22.3MB
```

코드 변경 후 새로 실행 (docker-compose up -d --build)

```bash
$ docker images
REPOSITORY           TAG            IMAGE ID       CREATED          SIZE
project/django       latest         66390b847cf4   48 seconds ago   647MB
<none>               <none>         bcd85ffe3187   9 minutes ago    647MB
project/django-dev   latest         7121aaf87ebe   3 hours ago      647MB
project/nginx        latest         ba7b66ec5f59   22 hours ago     22.3MB
```

위의 예시에서 볼 수 있듯이 소스코드를 변경하여 다시 컨테이너를 실행하면 새로운 이미지가 만들어져 66390b847cf4라는 새로운 IMAGE ID를 갖게 되고
기존의 bcd85ffe3187 IMAGE ID를 가진 이미지는 `<none>`으로 표시된다.

**위와 같이 `docker images` 명령어에서 `<none>`:`<none>`으로 보여지는 이미지들은 dangling 이미지로써 불필요한 디스크 용량을 차지할 수 있으므로 주기적으로 삭제해주는 것이 좋다.**
(단, `docker images -a`명령어를 통해서만 보여지는 `<none>`:`<none>`은 기존 이미지 레이어의 child 이미지로 용량 문제가 없다.)

사용하지 않고 dangling된 이미지만 명확히 찾기 위해 아래 명령어를 사용할 수도 있다.

```bash
$ docker images -f "dangling=true" -q
10a955570057 <--dangling된 이미지 ID를 리턴한다.
```

이와 같은 dangling된 이미지는 docker rmi명령어를 통해 삭제하면 된다.

```bash
$ docker rmi 10a955570057
```

만약 container에 연결되지 않은 image가 쌓여있다면 아래와 같은 명령어를 통해 삭제하면 된다.

```bash
$ docker image prune -a
WARNING! This will remove all images without at least one container associated to them.
Are you sure you want to continue? [y/N] y
```

## **Docker를 사용하지 않고 가상환경으로 실행 (pipenv & runserver)**

django 프로젝트 부분은 pipenv를 사용한 python 가상환경을 기준으로 작성되었음.
VSCode를 이용할 때, python interpreter부분은 pipenv shell을 실행하여 생성된 위치를 지정하면 됨
(ex. `~/.local/share/virtualenvs/django-Iohwxul1/bin/python`와 같은 형태로 생성되는 위치값 지정)

`makemigrations`, `migrate`, `collectstatic` 명령어들을 실행하기 위해서는 현재 상태에서는 pipenv를 이용한 가상환경 상태에서 실행해야함

pipenv 를 이용한 가상환경 활성화 명령어

```bash
$ pipenv shell
Loading .env environment variables...
Launching subshell in virtual environment...
 . /Users/example/.local/share/virtualenvs/django-DAeX99bh/bin/activate
➜  django git:(master) ✗  . /Users/example/.local/share/virtualenvs/django-DAeX99bh/bin/activate
(django) $  <-- 가상환경 활성화되면 쉘 앞에 (django)가 붙는다
```

docker를 사용하지 않고 pipenv 가상환경을 활성화한 상태에서 로컬 서버를 실행하고 싶을 때에는 아래의 명령어를 사용하면 된다.

```bash
(django) $ python manage.py runserver
```

---

# **Test Code**

pipenv 를 이용한 test code 실행 방법

```bash
$ pipenv shell
Loading .env environment variables...
Launching subshell in virtual environment...
 . /Users/example/.local/share/virtualenvs/django-DAeX99bh/bin/activate
➜  django git:(master) ✗  . /Users/example/.local/share/virtualenvs/django-DAeX99bh/bin/activate
(django) $  <-- 가상환경 활성화되면 쉘 앞에 (django)가 붙는다

(django) $ pytest <-- 입력시 작성한 test code 실행되어 검증 처리된다.

===================================================================================================================== test session starts =====================================================================================================================
platform darwin -- Python 3.8.13, pytest-7.2.0, pluggy-1.0.0
django: settings: project_api.settings (from ini)
rootdir: /Users/las/Desktop/project/project_server/django, configfile: pytest.ini
plugins: django-4.5.2
collected 15 items

project_api/apps/exercises/tests.py ..                                                                                                                                                                                                                     [ 13%]
project_api/apps/users/tests.py .............                                                                                                                                                                                                              [100%]

===================================================================================================================== 15 passed in 13.80s =====================================================================================================================
```

docker-compose exec 를 이용한 test code 실행 방법

```bash
$ docker-compose -f docker-compose-local.yml exec web sh

/usr/src/app # pytest <-- 입력시 작성한 test code 실행되어 검증 처리 된다.

===================================================================================================================== test session starts =====================================================================================================================
platform darwin -- Python 3.8.13, pytest-7.2.0, pluggy-1.0.0
django: settings: project_api.settings (from ini)
rootdir: /Users/las/Desktop/project/project_server/django, configfile: pytest.ini
plugins: django-4.5.2
collected 15 items

project_api/apps/exercises/tests.py ..                                                                                                                                                                                                                     [ 13%]
project_api/apps/users/tests.py .............                                                                                                                                                                                                              [100%]

===================================================================================================================== 15 passed in 13.80s =====================================================================================================================

```

# **Django 프로젝트 개선 및 추가 기능**

## **Django App 관련 디렉토리 구조**

기존 Django 관련 프로젝트에서는 Project 디렉토리와 App 디렉토리가 같은 depth에 있어 App이 늘어날 수록 Project 디렉토리와 App 디렉토리가 한눈에 구분되지 않음.

따라서 아래와 같이 프로젝트 디렉토리 하위에 apps 디렉토리를 만들어 해당 디렉토리에 app 디렉토리가 모이도록 구성
(apps/sample_app , apps/users 참고)

```bash
.
├── __init__.py
├── apps
│   ├── commons
│   ├── excercises
│   └── users
├── asgi.py
├── settings.py
├── urls.py
├── utils.py
└── wsgi.py
```

이와 같은 구조를 만들기 위해 프로젝트 디렉토리의 셋팅 파일 (settings.py) 내부에 하단의 셋팅 추가

```python
...
# Django App들을 apps directory에 모아서 처리하기위해 아래 system path를 추가해줌
sys.path.insert(0, os.path.join(BASE_DIR, "xxxxx_api/apps"))
...
```

참고로 app을 추가하기 위해서는 apps 디렉토리에 접근한 뒤에 아래와 같이 app 생성 명령어를 실행해야함

```python
(django) $ python manage.py startapp appname
```

---

# **API 문서 자동화**

Restful API를 구축하면 클라이언트단에서 API 문서를 참고하여 개발을 진행해야함.

API 문서를 매번 수동으로 작성하는 것은 비효율적일 수 있으니 swagger / redoc을 포함한 `drf_yasg` 패키지를 통해 문서 자동화를 진행 (본 스타터팩 프로젝트에서는 `/swagger` 혹은 `/redoc` 의 URL로 접근하여 확인 가능)

본 스타터팩에는 `drf_yasg` 패키지가 이미 설치되어 있으므로 아래의 문서와 적용 방법(자체 구현 방식)에 따라 진행하면 시간을 단축하여 효율적으로 문서화가 가능

## **1) 새로 app을 생성하게 되면 app 디렉토리 내부에 `doc_schemas.py` 파일 생성**

view에서 decorator로 간단히 불러서 사용하기 위함

`doc_schemas.py`는 각 app 디렉토리 하위에 하나씩 생성한다.

CBV로 작성하기 어렵거나 특별한경우 FBV의 API 문서 자동화를 사용하기 위함이다.

# CBV로 작성할 경우 각 app 디렉토리 하위에 serializers에 serializer를 작성한다.

(예시) users앱 내부의 `doc_schemas.py`

```bash
.
└── users
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── doc_schemas.py
    ├── forms.py
    ├── migrations
    ├── models.py
    ├── serializers.py
    ├── tests.py
    ├── urls.py
    ├── utils.py
    └── views.py
```

# FBV

```python
"""doc_schemas 모듈 설명

각 app별로 doc_schemas.py 모듈을 포함하여 해당 모듈내에서
변수로 각 API에 대한 request_body, response를 정의

정의된 값들은 views.py 내에서 각 API 상단에 데코레이터로 swagger / redoc 문서화에 필요한
request_body, response에 할당하여 사용
"""
from drf_yasg import openapi
from typing import Final

# /users/login API에서 문서화 (swagger / redoc)을 위해 사용하는 request_body & response
LOGIN_REQUEST_BODY: Final = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "phone": openapi.Schema(
            title="Phone Number",
            type=openapi.TYPE_STRING,
            description="`<= 20 characters`",
        ),
        "password": openapi.Schema(
            title="Password",
            type=openapi.TYPE_STRING,
            description="`8 <= & <= 128 characters`",
        ),
    },
    required=["phone", "password"],
)
LOGIN_RESPONSE: Final = {
    200: openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "token": openapi.Schema(
                title="Token",
                type=openapi.TYPE_STRING,
                description="Token string",
            ),
        },
    )
}
```

# CBV

```python
"""serializer

각 app별로 serilizers.py 모듈을 포함하여 해당 모듈내에서
변수로 각 API에 대한 request_body, response를 정의

정의된 값들은 views.py 내에서 각 API 상단에 데코레이터로 swagger / redoc 문서화에 필요한
request_body, response에 할당하여 사용
"""

from rest_framework import serializers

class SettingDataResponseSerializer(serializers.Serializer):
    push_notifications = serializers.BooleanField(required=False)
    google_authenticator = serializers.BooleanField(required=False)
    receive_promotional_email = serializers.BooleanField(required=False)

```

## **2) View에 decorator 및 주석 작성, CBV & FBV 차이**

decorator와 주석을 설정해주지 않아도 문서에서 리스팅은 되지만 내용은 없는 상태로 리스팅 됨.

decorator와 주석을 작성해주어야 비로소 제대로 문서화된 형태를 볼 수 있음.

FBV

- decorator 설정을 위해 필요한 모듈 추가 (`swagger_auto_schema`) &&
- 위에서 생성한 `doc_schemas.py`의 내용을 사용하기 위해 `views.py`에서 `doc_schemas`모듈 추가

CBV

- decorator 설정을 위해 필요한 모듈 추가 (`swagger_auto_schema`) &&
- `request_body`, `response_body`를 위한 serializers 추가

- 필요한 View의 상단에 decorator 및 주석 작성

project 프로젝트에서는 Class-based View(CBV)를 사용을 권장하고 Class-based View(CBV)보다 Function-based View(FBV)가 효율1 적인 경우에는 예외로 FBV를 사용한다

# CBV

```python
class [클래스 명칭](APIView):
    """
    [뷰 메소드 형태]:[API 설명]
    ---
    ## [API에 대한 상세 설명]
    """
    permission_classes = [permissions.IsAuthenticated]

    @method_decorator(
        name="get",  # API 사용 메소드 (여러 메소드를 사용하는 경우엔 메소드 별로 추가)
        decorator=swagger_auto_schema(
            request_body=None(), # 해당 메소드의 리퀘스트 바디 내용(각각 serializers에 정의)
            responses={200: SettingDataResponseSerializer}, # 해당 메소드의 리스폰스 내용(각각 serializers에 정의)
        ),
    )
    def get(self, request):
        ... 뷰 내용 생략 ...
```

#### 예시

```python

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
        ... 하단 생략 ...


```

# FBV

```python
@swagger_auto_schema(
    method="post",  # API 사용 메소드 (여러 메소드를 사용하는 경우엔 메소드 별로 추가)
    request_body=ds.LOGIN_REQUEST_BODY, # 해당 메소드의 리퀘스트 바디 내용(doc_schemas.py에 정의)
    responses=ds.LOGIN_RESPONSE, # 해당 메소드의 리스폰스 내용(doc_schemas.py에 정의)
)
@api_view(["POST"])
@permission_classes((permissions.AllowAny,))
def [뷰명칭](request):
    """
    [뷰 메소드 형태]:[API 설명]

    ---
    ## [API에 대한 상세 설명]
    """
		... 뷰 내용 생략 ...
```

#### 예시

```python
@swagger_auto_schema(
    method="post",
    request_body=ds.LOGIN_REQUEST_BODY,
    responses=ds.LOGIN_RESPONSE,
)
@api_view(["POST"])
@permission_classes((permissions.AllowAny,))
def login(request):
    """
    post:타입별 커스텀 유저 로그인 API

    ---
    ## API URL: `/users/login/`
    """
    phone = request.data.get("phone")
    password = request.data.get("password")

		... 하단 생략 ...
```

# **코드 스타일 통일을 위한 자동 lint & format & import sort**

여러명이 같이 작업을 할때 Python 코드 스타일을 PEP8에 맞게 구성하여 코드 품질을 향상시키기 위함.

사용 패키지: pre-commit (lint 자동화를 위한 autoflake, lint를 위해 flake8, 자동 formatting을 위해 black을 내부적으로 사용, import 순서를 자동으로 정렬해주는 isort 사용)

pre-commit에 대한 설정 파일은 django/.pre-commit-config.yaml에 적혀있다.

정상적으로 동작하는 경우 `git commit`시 PEP8에 맞지 않는 형태가 있으면 아래와 같이 에러를 출력하며 자동으로 코드를 바꿔줌

- .pre-commit-config.yaml 구성

repo: 리포지토리
rev: 버전
hooks: 호출할 pre-commit 기능
args: 상세 설정 및, 설정 파일

```yaml
# See https://pre-commit.com for more information
# See https://pre-commit.com/hooks.html for more hooks
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: check-yaml
      - id: check-json
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        description: "Black: The uncompromising Python code formatter"
        entry: black
        language: python
        minimum_pre_commit_version: 2.9.2
        require_serial: true
        types_or: [python, pyi]
    language_version: python3.8
  - repo: https://github.com/myint/autoflake
    rev: v2.0.1
    hooks:
      - id: autoflake
        args:
          - --remove-unused-variables
          - --remove-all-unused-imports
  - repo: https://github.com/PyCQA/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: ["--config=django/setup.cfg"]
        description: "`flake8` is a command-line utility for enforcing style consistency across Python projects."
        entry: flake8
        language: python
        types: [python]
        require_serial: true
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        name: isort (python)
```

- `git commit` 실행 예시

```bash
➜  django git:(master) ✗ git commit
[WARNING] The 'rev' field of repo 'https://github.com/ambv/black' appears to be a mutable reference (moving tag / branch).  Mutable references are never updated after first install and are not supported.  See https://pre-commit.com/#using-the-latest-version-for-a-repository for more details.
black....................................................................Failed
- hook id: black
- files were modified by this hook

reformatted django/test.py
All done! ✨ 🍰 ✨
1 file reformatted.

flake8...................................................................Passed
```

- 자동으로 변경된 파일 예시

```bash
diff --git a/django/test.py b/django/test.py
index 5e27e24..8adb325 100644
--- a/django/test.py
+++ b/django/test.py
@@ -1,5 +1,5 @@
-hello ="123"
-bye= 'asdf'
+hello = "123"
+bye = "asdf"

-print('hello = ', hello)
-print('bye = ', bye)
+print("hello = ", hello)
+print("bye = ", bye)
```

- 전체 파일 pre-commit 실행 시키고싶을시

```bash
pre-commit run --all-files
```

실행시키면 도비니다.

# **i18n(localization) 설명**

# Django 전역 설정

settings.py 파일의 내용을 수정 및 추가한다.

미들웨어 설정

settings.py 파일에서 아래와 같이 SessionMiddleware와 CommonMiddleware 사이에 LocaleMiddleware를 추가한다.

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

기본 언어 설정

settings.py 파일에서 다음 내용을 수정한다.

```python
LANGUAGE_CODE = 'ko-KR'
```

settings.py 파일에서 상단에 다음과 같이 import문을 추가한다.

```python
from django.utils.translation import ugettext_lazy as _
```

프로젝트에서 지원할 다국어 언어값을 설정한다.

```python
LANGUAGES = [
    ('ko', _('Korean')),
    ('en', _('English')),
]
```

번역 파일이 들어있는 locale 디렉토리를 지정하고 실제로 디렉토리도 만들도록 한다.

```python
LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)
```

번역 파일 만들기

```
번역파일 상위 공통 로직

# SOME DESCRIPTIVE TITLE.
# Copyright (C) YEAR THE PACKAGE'S COPYRIGHT HOLDER
# This file is distributed under the same license as the PACKAGE package.
# FIRST AUTHOR <EMAIL@ADDRESS>, YEAR.
#
#, fuzzy
msgid ""
msgstr ""
"Project-Id-Version: PACKAGE VERSION\n"
"Report-Msgid-Bugs-To: \n"
"POT-Creation-Date: 2023-01-11 14:49+0900\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\n"
"Language-Team: LANGUAGE <LL@li.org>\n"
"Language: \n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Plural-Forms: nplurals=2; plural=(n != 1);\n"
```

아래 명령어로 전체 메시지 파일을 만들 수 있다.

python manage.py makemessage -a
그러나 최초에는 잘 동작하지 않아서 아래와 같이 개별적으로 메시지 파일을 생성한다.

```
영문 번역 파일 예시

#: project_api/apps/users/serializers.py:77
msgid "This account is registered by social authentication login already"
msgstr "This account is registered by social authentication login already"

```

```
한글 번역 파일 예시

#: project_api/apps/users/serializers.py:77
msgid "This account is registered by social authentication login already"
msgstr "이 계정은 이미 가입된 이메일 계정입니다."

```

python manage.py makemessages -l ko
python manage.py makemessages -l en
메시지 파일 컴파일

생성한 번역 파일을 Django가 인식할 수 있도록 컴파일한다.

python manage.py compilemessages
컴파일 후에는 Django 서버를 재기동해야 메시지 번역 결과가 반영된다.

코드내의
/django/locale 참고

# 주의할 사항

번역 처리가 안 되는 것처럼 보이는 fuzzy 플래그

.po 메시지 파일에 주석으로 #, fuzzy 표시가 있으면 해당 문자열은 번역되지 않는다. 따라서 번역 문자열 상단에 주석으로 #, fuzzy 표시가 있으면 해당 부분의 주석을 삭제한다.

주석이기 때문에 컴파일 결과에 영향을 미치지 않을 것 같지만 실제로는 번역되지 않아 원인을 찾는데 시간을 많이 소비할 수 있다.

---

[Learn Markdown](https://bitbucket.org/tutorials/markdowndemo)

[py]: https://project-images.s3.ap-northeast-2.amazonaws.com/uploaded-images/etc/python.png
[po]: https://project-images.s3.ap-northeast-2.amazonaws.com/uploaded-images/etc/postgresql.png
[ng]: https://project-images.s3.ap-northeast-2.amazonaws.com/uploaded-images/etc/nginx.png
[do]: https://project-images.s3.ap-northeast-2.amazonaws.com/uploaded-images/etc/docker.png
[ec]: https://project-images.s3.ap-northeast-2.amazonaws.com/uploaded-images/etc/ec2.png
[s3]: https://project-images.s3.ap-northeast-2.amazonaws.com/uploaded-images/etc/s3.png
[cf]: https://project-images.s3.ap-northeast-2.amazonaws.com/uploaded-images/etc/cloudfront.png
[rt]: https://project-images.s3.ap-northeast-2.amazonaws.com/uploaded-images/etc/route53.png
[se]: https://project-images.s3.ap-northeast-2.amazonaws.com/uploaded-images/etc/ses.png
[sn]: https://project-images.s3.ap-northeast-2.amazonaws.com/uploaded-images/etc/sns.png
[er]: https://project-images.s3.ap-northeast-2.amazonaws.com/uploaded-images/etc/ecr.png
