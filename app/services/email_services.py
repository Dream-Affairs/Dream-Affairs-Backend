"""This module is used to send an email to the recipient."""
import smtplib
import ssl
from email.message import EmailMessage

import pystache
from mjml import mjml_to_html

from app.core.config import settings

EMAIL_NAME = settings.EMAIL_NAME
EMAIL_ADDRESS = settings.EMAIL_ADDRESS
EMAIL_PASSWORD = settings.EMAIL_PASSWORD
EMAIL_HOST = settings.EMAIL_HOST
EMAIL_PORT = settings.EMAIL_PORT


def send_email(username: str, recipient_address: str) -> None:
    """This function is used to send an email to the recipient."""
    msg = EmailMessage()
    msg["Subject"] = "HelpMeOut Screen Recorder"
    # msg["From"] = formataddr((EMAIL_NAME, EMAIL_ADDRESS))
    msg["To"] = recipient_address

    with open("app/services/video_mail.mjml", "rb") as f:
        mail = mjml_to_html(f)

    mail = mail.html
    context = {
        "username": username,
    }
    mail = pystache.render(mail, context)

    msg.set_content(mail, subtype="html")

    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as smtp:
        smtp.starttls(context=ssl.create_default_context())
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)
