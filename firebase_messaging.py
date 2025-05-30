import firebase_admin
from firebase_admin import credentials, messaging

cred = credentials.Certificate("techcontrol_notification.json")
firebase_admin.initialize_app(cred)

def sendNotification(tokenMessage: str, titleMessage: str, bodyMessage: str):
    registration_token = tokenMessage

    message = messaging.Message(
        token=registration_token,
        notification=messaging.Notification(
            title=titleMessage,
            body=bodyMessage,
        ),
        android=messaging.AndroidConfig(
            priority="high",
            ttl=60 * 60 * 24 * 7 * 4,  # 4 semanas em segundos
            notification=messaging.AndroidNotification(
                tag="alerta_techcontrol",
                channel_id="Ttechcontrol_alerts",
            ),
        ),
        apns=messaging.APNSConfig(
            headers={
                "apns-priority": "10"
            },
            payload=messaging.APNSPayload(
                aps=messaging.Aps(
                    alert=messaging.ApsAlert(
                        title=titleMessage,
                        body=bodyMessage
                    ),
                    badge=1,
                    sound="default",
                    content_available=True,
                    category="ALERTA_TECHCONTROL"
                )
            )
        ),
        webpush=messaging.WebpushConfig(
            headers={
                "TTL": "0"
            },
            notification=messaging.WebpushNotification(
                title=titleMessage,
                body=bodyMessage
            ),
        ),
        fcm_options=messaging.FCMOptions(
            analytics_label="alerta_techcontrol_notificacao"
        )
    )

    print(message)
    response = messaging.send(message)
    print('<--->Mensagem enviada com sucesso:<--->', response)
