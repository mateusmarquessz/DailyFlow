import logging
import smtplib
from email.message import EmailMessage

from app.core.config import settings

logger = logging.getLogger("dailyflow.email")


def send_email(to_email: str, subject: str, body: str) -> None:
    """Sends a plain-text email via SMTP when configured.

    Falls back to logging the message in development so the password-reset flow
    can be exercised without a real mail provider. Plug a transactional email
    provider (SMTP credentials, SES, SendGrid, ...) via the SMTP_* env vars in production.
    """
    if not settings.smtp_host:
        logger.info("SMTP not configured — logging email instead.\nTo: %s\nSubject: %s\n%s", to_email, subject, body)
        return

    message = EmailMessage()
    message["From"] = settings.smtp_from_email
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.starttls()
        if settings.smtp_user and settings.smtp_password:
            server.login(settings.smtp_user, settings.smtp_password)
        server.send_message(message)
