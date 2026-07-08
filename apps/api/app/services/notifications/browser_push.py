import json

from pywebpush import WebPushException, webpush

from app.core.config import settings


def send_browser_push(subscription_info: dict, title: str, body: str, url: str | None = None) -> None:
    try:
        webpush(
            subscription_info=subscription_info,
            data=json.dumps({"title": title, "body": body, "url": url}),
            vapid_private_key=settings.vapid_private_key,
            vapid_claims={"sub": settings.vapid_subject},
        )
    except WebPushException:
        # Subscription likely expired/revoked; the caller should prune it
        # from the user's stored subscriptions on repeated failures.
        raise
