from django.db import models
from django.utils.translation import ugettext_lazy as _


class ExerciseRecord(models.Model):
    """
    운동 기록
    """

    start_datetime = models.DateTimeField(verbose_name="운동 날짜")
    total_distance = models.FloatField(verbose_name="운동 거리")
    total_time = models.TimeField(verbose_name="운동 시간")
    average_speed = models.FloatField(verbose_name="운동 평균 속도")
    total_calories = models.FloatField(verbose_name="운동 칼로리")
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True)
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
    )


class ExerciseDetailRecord(models.Model):
    """
    운동 상세 기록
    """

    start_time = models.DateTimeField(verbose_name="운동 시작 시간")
    duration = models.IntegerField(verbose_name="지속 시간(초)")
    distance = models.FloatField(verbose_name="이동한 거리")
    heart_rate = models.PositiveSmallIntegerField(verbose_name="심장 박동수")
    altitude = models.FloatField(
        verbose_name="고도",
        null=True,
    )
    latitude = models.FloatField(
        verbose_name="위도",
        null=True,
    )
    longitude = models.FloatField(
        verbose_name="경도",
        null=True,
    )
    speed = models.FloatField(verbose_name="속도")
    exercise_recode = models.ForeignKey(
        ExerciseRecord,
        on_delete=models.CASCADE,
        related_name="exercise_detail_record",
    )
