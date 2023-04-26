"""doc_schemas 모듈 설명

각 app별로 doc_schemas.py 모듈을 포함하여 해당 모듈내에서
변수로 각 API에 대한 request_body, response를 정의

정의된 값들은 views.py 내에서 각 API 상단에 데코레이터로 swagger / redoc 문서화에 필요한
request_body, response에 할당하여 사용
"""
from typing import Final

from drf_yasg import openapi

# /users/login API에서 문서화 (swagger / redoc)을 위해 사용하는 request_body & response
EXERCISE_RECORD_ID_QUERY_PARAMETER = openapi.Parameter(
    "exercise_record_id",
    openapi.IN_PATH,
    required=True,
    description="운동기록 아이디",
    type=openapi.TYPE_STRING,
)
