import logging
import smtplib
from email.message import EmailMessage

from flask import current_app


logger = logging.getLogger(__name__)


def send_password_reset_email(recipient, reset_url):
    """Send a password-reset email via SMTP, without logging the secret link."""
    if current_app.config["MAIL_SUPPRESS_SEND"]:
        logger.info("Password-reset email suppressed by local development configuration.")
        return

    mail_server = current_app.config.get("MAIL_SERVER")
    sender = current_app.config.get("MAIL_DEFAULT_SENDER")
    if not mail_server or not sender:
        raise RuntimeError("Email delivery is not configured.")

    message = EmailMessage()
    message["Subject"] = "Reset your SupportSphere password"
    message["From"] = sender
    message["To"] = recipient
    message.set_content(
        "We received a password reset request for your SupportSphere account.\n\n"
        f"Reset your password: {reset_url}\n\n"
        "This link expires in 30 minutes and can only be used once. If you did not request it, you can ignore this email."
    )
    with smtplib.SMTP(mail_server, current_app.config["MAIL_PORT"], timeout=10) as smtp:
        if current_app.config["MAIL_USE_TLS"]:
            smtp.starttls()
        username = current_app.config.get("MAIL_USERNAME")
        if username:
            smtp.login(username, current_app.config.get("MAIL_PASSWORD", ""))
        smtp.send_message(message)
