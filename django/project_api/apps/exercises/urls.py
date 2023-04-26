from django.urls import path

from .views import ExerciseRecordAPIView, ExerciseRecordView

urlpatterns = [
    path(
        "record/",
        ExerciseRecordAPIView.as_view(),
        name="exercise-record",
    ),
    path(
        "record/<int:exercise_record_id>/",
        ExerciseRecordView.as_view(),
        name="exercise-record-view",
    ),
]
