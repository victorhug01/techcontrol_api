import firebase_admin
from firebase_admin import credentials, messaging

cred = credentials.Certificate("techcontrol_notification.json")
firebase_admin.initialize_app(cred)
payload = {
    "route": "/home"  # A chave 'route' carrega a rota desejada
}
def sendNotification(tokenMessage : str, titleMessage: str, bodyMessage : str):
    registration_token = tokenMessage

    message = messaging.Message(
        notification=messaging.Notification(
            title = titleMessage,
            body = bodyMessage,
        ),
        token=registration_token,
        data=payload if payload else {}
    )
    print(message)
    response = messaging.send(message)
    print('<--->Mensagem enviada com sucesso:<--->', response)


