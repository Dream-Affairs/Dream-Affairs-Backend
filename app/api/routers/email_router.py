"""This module contains the email router services for the API."""
from typing import Any, Dict

from fastapi import APIRouter, status

from app.services.email_services import send_email_api

email_router = APIRouter(prefix="/email")


@email_router.post(
    "/send-email",
    status_code=status.HTTP_200_OK,
    tags=["Email"],
)
def send_email(
    kwargs: Dict[str, Any],
    subject: str,
    recipient: str,
    sender: str,
    sender_name: str,
    template: str,
) -> None:
    """This function is used to send an email to the recipient using the API.

    Args:
        subject: This is the subject of the email.
        recipient: This is the email address of the recipient.
        sender: This is the email address of the sender. \
            It is the email in the env file.
        sender_name: This is the name of the sender. \
            It is the name in the env file.
        template: This is the template of the email.
    """
    send_email_api(
        subject, recipient, sender, sender_name, template, kwargs=kwargs
    )
