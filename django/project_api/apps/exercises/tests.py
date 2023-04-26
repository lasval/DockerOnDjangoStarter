import json
from pathlib import Path

from conftest import unauthorized_after_login
from rest_framework import status
from rest_framework.test import APITestCase

from django.urls import reverse


class UsersTest(APITestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_exercise_recode_save(self):
        """운동기록 저장 테스트"""

        exercise_recode_save_url = reverse("exercise-record")

        file_path = (
            Path(__file__).resolve().parent / "ex_exercise_recode_save_req_body.json"
        )

        with open(file_path, "r") as file:
            exercise_recode_save_req_body = json.load(file)

        response = self.client.post(
            exercise_recode_save_url,
            exercise_recode_save_req_body,
            format="json",
        )
        unauthorized_after_login(self, response)

        response = self.client.post(
            exercise_recode_save_url,
            exercise_recode_save_req_body,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=None)

    def test_exercise_recode_list(self):
        """운동기록 리스트 조회 테스트"""

        exercise_recode_list_url = reverse("exercise-record")
        response = self.client.get(exercise_recode_list_url)
        unauthorized_after_login(self, response)

        response = self.client.get(exercise_recode_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=None)
