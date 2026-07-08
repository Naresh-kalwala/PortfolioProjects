from twilio.rest import Client

from app.core.config import settings


def send_whatsapp(body: str, to_number: str | None = None) -> None:
    client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
    client.messages.create(
        from_=settings.twilio_whatsapp_from,
        to=to_number or settings.notify_whatsapp_to,
        body=body,
    )
