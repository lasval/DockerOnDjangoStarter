import os

import requests


class SlackWebhook:
    def __init__(self, text) -> None:
        self.text = text

    def slack_error_handler(text):
        env = os.environ.get("ENVIRONMENT").upper()

        # webhook url
        url = os.environ.get("SLACK_WEBHOOK_URL")

        payload = {"username": f"project-{env}-WEBHOOK", "text": text}

        r = requests.post(url, json=payload)

        print(r)
