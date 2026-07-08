import smtplib
from email.mime.text import MIMEText

from app.core.config import settings


def send_email(to_address: str, subject: str, body: str) -> None:
    if settings.email_backend == "ses":
        _send_via_ses(to_address, subject, body)
    else:
        _send_via_smtp(to_address, subject, body)


def _send_via_smtp(to_address: str, subject: str, body: str) -> None:
    message = MIMEText(body)
    message["Subject"] = subject
    message["From"] = settings.email_from
    message["To"] = to_address

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.starttls()
        if settings.smtp_username:
            server.login(settings.smtp_username, settings.smtp_password)
        server.sendmail(settings.email_from, [to_address], message.as_string())


def _send_via_ses(to_address: str, subject: str, body: str) -> None:
    import boto3

    client = boto3.client("ses", region_name=settings.aws_region)
    client.send_email(
        Source=settings.email_from,
        Destination={"ToAddresses": [to_address]},
        Message={
            "Subject": {"Data": subject},
            "Body": {"Text": {"Data": body}},
        },
    )
