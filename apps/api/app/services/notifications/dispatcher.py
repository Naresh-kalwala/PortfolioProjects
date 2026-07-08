import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.enums import NotificationChannel, NotificationType
from app.models.notification import Notification
from app.models.user import UserProfile
from app.services.notifications.browser_push import send_browser_push
from app.services.notifications.email import send_email
from app.services.notifications.whatsapp import send_whatsapp

logger = logging.getLogger(__name__)

_CHANNEL_SENDERS = {
    NotificationChannel.EMAIL: "email",
    NotificationChannel.WHATSAPP: "whatsapp",
    NotificationChannel.BROWSER_PUSH: "browser_push",
}


def dispatch_notification(
    session: Session,
    user: UserProfile,
    notification_type: NotificationType,
    title: str,
    body: str,
    related_job_id: str | None = None,
    url: str | None = None,
) -> None:
    preferences = user.notification_preferences or {}

    for channel, pref_key in _CHANNEL_SENDERS.items():
        if not preferences.get(pref_key, False):
            continue

        notification = Notification(
            user_id=user.id,
            type=notification_type,
            channel=channel,
            title=title,
            body=body,
            related_job_id=related_job_id,
        )
        session.add(notification)

        try:
            if channel == NotificationChannel.EMAIL:
                send_email(user.email, title, body)
            elif channel == NotificationChannel.WHATSAPP and user.whatsapp_number:
                send_whatsapp(f"{title}\n{body}", to_number=user.whatsapp_number)
            elif channel == NotificationChannel.BROWSER_PUSH:
                for subscription in user.push_subscriptions or []:
                    send_browser_push(subscription, title, body, url)
            notification.sent_at = datetime.now(timezone.utc)
        except Exception as exc:  # noqa: BLE001 - one channel failing must not block others
            logger.exception("Failed to send %s notification to user %s", channel, user.id)
            notification.delivery_error = str(exc)

    session.commit()
