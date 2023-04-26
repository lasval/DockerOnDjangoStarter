from datetime import datetime

from project_api.utils import UnprocessableEntityError, get_serilaizer_check
from drf_yasg.utils import swagger_auto_schema
from exercises.models import ExerciseDetailRecord, ExerciseRecord
from exercises.serializers import (
    ExerciseDetailRecordSerializer,
    ExerciseRecordListSerializer,
    ExerciseRecordSaveSerializer,
    ExerciseRecordSerializer,
)
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from django.db import transaction
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy


class ExerciseRecordAPIView(APIView):
    """
    post: 운동기록 저장 API

    - HTTP Header에 api-key Token 필요
        key: Authorization, value: Token [토큰값] (예시: Authorization: Token c5a4e25a7c5d8dc545c8d10740bfe655429c129b)

    get: 운동기록 리스트 조회 API

    - HTTP Header에 api-key Token 필요
        key: Authorization, value: Token [토큰값] (예시: Authorization: Token c5a4e25a7c5d8dc545c8d10740bfe655429c129b)

    """

    permission_classes = [permissions.IsAuthenticated]

    @method_decorator(
        name="post",
        decorator=swagger_auto_schema(
            request_body=ExerciseRecordSaveSerializer(), responses={200: ""}
        ),
    )
    def post(self, request):
        serializer = get_serilaizer_check(ExerciseRecordSaveSerializer, request.data)
        detail = []

        with transaction.atomic():
            exercise_record = ExerciseRecord.objects.create(
                start_datetime=serializer.data.get("start_datetime", None),
                total_distance=serializer.data.get("total_distance", None),
                total_time=serializer.data.get("total_time", None),
                average_speed=serializer.data.get("average_speed", None),
                total_calories=serializer.data.get("total_calories", None),
                user=request.user,
            )
            detail_serializer = serializer.data.get("detail", None)

            for item in detail_serializer:
                detail.append(
                    ExerciseDetailRecord(
                        **item,
                        exercise_recode=exercise_record,
                    )
                )

            ExerciseDetailRecord.objects.bulk_create(detail)

            return Response(status=status.HTTP_200_OK)

    @method_decorator(
        name="get",
        decorator=swagger_auto_schema(
            request_body=None,
            responses={200: ExerciseRecordListSerializer(many=True)},
        ),
    )
    def get(self, request):
        exercise_record_serializer = ExerciseRecordSerializer(
            ExerciseRecord.objects.filter(
                user_id=request.user.id, deleted_at__isnull=True
            ).values(
                "id",
                "start_datetime",
                "total_distance",
                "total_time",
                "average_speed",
                "total_calories",
            ),
            many=True,
        )

        return Response(status=status.HTTP_200_OK, data=exercise_record_serializer.data)


class ExerciseRecordView(APIView):
    """
    get: 운동기록 상세 조회 API

    - HTTP Header에 api-key Token 필요
        key: Authorization, value: Token [토큰값] (예시: Authorization: Token c5a4e25a7c5d8dc545c8d10740bfe655429c129b)

    - exercise_recode_id
        - 리스트 조회시 나오는 id값으로 보내주시면됩니다.

    delete: 운동기록 삭제 API

    - HTTP Header에 api-key Token 필요
        key: Authorization, value: Token [토큰값] (예시: Authorization: Token c5a4e25a7c5d8dc545c8d10740bfe655429c129b)

    - exercise_recode_id
        - 리스트 조회시 나오는 id값으로 보내주시면됩니다.

    """

    permission_classes = [permissions.IsAuthenticated]

    @method_decorator(
        name="get",
        decorator=swagger_auto_schema(
            request_body=None,
            responses={200: ExerciseRecordSerializer()},
        ),
    )
    def get(self, request, exercise_record_id):
        try:
            record = ExerciseRecord.objects.get(
                pk=exercise_record_id, deleted_at__isnull=True
            )
        except ExerciseRecord.DoesNotExist:
            return UnprocessableEntityError(
                message=ugettext_lazy("Exercise dose not exists"),
            )

        exercise_detail_record = ExerciseDetailRecordSerializer(
            record.exercise_detail_record.values(
                "start_time",
                "duration",
                "distance",
                "heart_rate",
                "altitude",
                "latitude",
                "longitude",
                "speed",
            ),
            many=True,
        ).data

        exercise_record_serializer = ExerciseRecordSerializer(
            {
                "id": exercise_record_id,
                "start_datetime": record.start_datetime,
                "total_distance": record.total_distance,
                "total_time": record.total_time,
                "average_speed": record.average_speed,
                "total_calories": record.total_calories,
                "user": {
                    "id": request.user.id,
                    "nickname": request.user.nickname,
                },
                "detail": exercise_detail_record,
            }
        )

        return Response(status=status.HTTP_200_OK, data=exercise_record_serializer.data)

    @method_decorator(
        name="delete",
        decorator=swagger_auto_schema(
            request_body=None,
            responses=None,
        ),
    )
    def delete(self, request, exercise_record_id):
        user = request.user

        try:
            exercise_record = ExerciseRecord.objects.get(pk=exercise_record_id)
        except ExerciseRecord.DoesNotExist:
            return UnprocessableEntityError(
                message=ugettext_lazy("Exercise dose not exists")
            )

        if exercise_record.user != user:
            return UnprocessableEntityError(
                message=ugettext_lazy("Exercise user dose not match"),
            )

        with transaction.atomic():
            exercise_record.deleted_at = datetime.now()

            exercise_record.save(update_fields=["deleted_at"])

        return Response(status=status.HTTP_200_OK)
