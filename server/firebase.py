import firebase_admin
from firebase_admin import credentials, auth, messaging
import os
from utils.config import get_settings

settings = get_settings()
cred_path = os.getenv('FIREBASE_CONFIG')
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)

def verify_firebase_token(id_token: str):
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        raise ValueError("Invalid or expired token")

#Single Notification
def send_push_notification(token: str, title: str, body: str):
    try:
        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            token=token
        )
        return messaging.send(message)
    except Exception as e:
        raise ValueError(str(e))

#Send Multiple Notifications
def send_bulk_notifications(tokens: list[str], title: str, body: str):
    message = messaging.MulticastMessage(
        notification=messaging.Notification(title=title, body=body),
        tokens=tokens
    )
    return messaging.send_multicast(message)

