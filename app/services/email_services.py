"""This module is used to send an email to the recipient."""
import smtplib
import ssl
from email.message import EmailMessage
from typing import Any, Dict, Tuple

import pystache
from mjml import mjml_to_html

from app.core.config import settings

EMAIL_NAME: str = settings.EMAIL_NAME
EMAIL_ADDRESS: str = settings.EMAIL_ADDRESS
EMAIL_PASSWORD: str = settings.EMAIL_PASSWORD
EMAIL_HOST: str = settings.EMAIL_HOST
EMAIL_PORT: int = settings.EMAIL_PORT


def send_email(
    msg: EmailMessage,
) -> None:
    """This function is used to send an email to the recipient.

    Args:
        msg: This is the email message object.
    """
    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as smtp:
        smtp.starttls(context=ssl.create_default_context())
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)
        # close connection
        smtp.quit()


def send_email_api(
    subject: str,
    recipient: str,
    sender: str,
    sender_name: str,
    template: str,
    **kwargs: Dict[str, Any],
) -> None:
    """This function is used to send an email to the recipient using the API.

    Args:
        subject: This is the subject of the email.
        body: This is the body of the email.
        recipient: This is the email address of the recipient.
        sender: This is the email address of the sender.
        sender_name: This is the name of the sender.
    """
    msg = EmailMessage()

    print(kwargs)
    body = mjml_to_html(pystache.render(template, kwargs.get("kwargs"))).html

    msg["Subject"] = subject
    msg["From"] = formataddr((sender_name, sender))
    msg["To"] = recipient
    msg.set_content(body, subtype="html")
    send_email(msg)


def send_company_email_api(
    subject: str,
    template: str,
    **kwargs: Dict[str, Any],
) -> None:
    """This function is used to send company specific emails to the recipient
    using the API.

    Args:
        subject: This is the subject of the email.
        template: This is the template of the email.
        **kwargs: This is the dictionary of the arguments.
    """
    msg = EmailMessage()

    # check if reciepient email is provided in the kwargs
    if not kwargs.get("recipient_email"):
        print("recipient_email is required in the kwargs!")
        return

    msg["Subject"] = subject
    msg["From"] = formataddr((EMAIL_NAME, EMAIL_ADDRESS))

    msg["To"] = kwargs.get("recipient_email")

    body = mjml_to_html(pystache.render(template, kwargs)).html

    msg.set_content(body, subtype="html")

    send_email(msg)


def formataddr(address: Tuple[str, str]) -> str:
    """This function is used to format the email address."""
    name, email_address = address
    return f"{name} <{email_address}>"
