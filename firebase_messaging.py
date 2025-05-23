import firebase_admin
from firebase_admin import credentials, messaging

def sendNotification(tokenMessage : str, titleMessage: str, bodyMessage : str):
    cred = credentials.Certificate("techcontrol_notification.json")
    firebase_admin.initialize_app(cred)

    registration_token = tokenMessage

    message = messaging.Message(
        notification=messaging.Notification(
            title = titleMessage,
            body = bodyMessage,
        ),
        token=registration_token,
    )
    response = messaging.send(message)
    print('Mensagem enviada com sucesso:', response)


