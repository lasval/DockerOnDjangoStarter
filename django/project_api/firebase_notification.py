from project_api.utils import StandardException
from firebase_admin import messaging

from django.utils.translation import ugettext_lazy


class FirebaseAppPush:
    def __init__(self, registration_token, title: str, body: str, data=None):
        self.registration_token = registration_token
        self.title = title
        self.body = body
        self.data = data

    def default_single_send_notification(self):
        message = messaging.Message(
            notification=messaging.Notification(
                title=self.title,
                body=self.body,
            ),
            data=self.data,
            token=self.registration_token,
        )
        try:
            response = messaging.send(message)
        except messaging.UnregisteredError:
            raise StandardException(
                422,
                ugettext_lazy("registration_token does not match"),
            )

        return response

    def default_multi_send_notification(self):
        assert isinstance(self.registration_token, list)

        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=self.title,
                body=self.body,
            ),
            data=self.data,
            token=self.registration_token,
        )
        try:
            response = messaging.send_multicast(message)
        except messaging.UnregisteredError:
            raise StandardException(
                422,
                ugettext_lazy("registration_token does not match"),
            )

        return response
