from exercises.models import ExerciseRecord
from rest_framework import serializers
from users.serializers import UserSimpleSerializer


class ExerciseDetailRecordSerializer(serializers.Serializer):
    start_time = serializers.DateTimeField()
    duration = serializers.IntegerField()
    distance = serializers.FloatField()
    heart_rate = serializers.IntegerField()
    altitude = serializers.FloatField(allow_null=True)
    latitude = serializers.FloatField(allow_null=True)
    longitude = serializers.FloatField(allow_null=True)
    speed = serializers.FloatField()


class ExerciseRecordSaveSerializer(serializers.Serializer):
    start_datetime = serializers.DateTimeField()
    total_distance = serializers.FloatField()
    total_time = serializers.TimeField()
    average_speed = serializers.FloatField()
    total_calories = serializers.FloatField()
    detail = ExerciseDetailRecordSerializer(many=True)


class ExerciseRecordSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    start_datetime = serializers.DateTimeField(required=False)
    total_distance = serializers.FloatField(required=False)
    total_time = serializers.TimeField(required=False)
    average_speed = serializers.FloatField(required=False)
    total_calories = serializers.FloatField(required=False)
    user = UserSimpleSerializer(required=False)
    detail = ExerciseDetailRecordSerializer(many=True, required=False)


class ExerciseRecordListSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    start_datetime = serializers.DateTimeField(required=False)
    total_distance = serializers.FloatField(required=False)
    total_time = serializers.TimeField(required=False)
    average_speed = serializers.FloatField(required=False)
    total_calories = serializers.FloatField(required=False)
