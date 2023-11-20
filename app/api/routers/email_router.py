"""This module contains the email router services for the API."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.schemas.email_schemas import EmailSchema
from app.database.connection import get_db
from app.services.email_services import send_company_email_api

email_router = APIRouter(prefix="/email")


@email_router.post(
    "/send-email",
    status_code=status.HTTP_200_OK,
    tags=["Email"],
)
def send_email(
    request: EmailSchema,
    db: Session = Depends(get_db),
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
    send_company_email_api(
        request.subject,
        request.recipient,
        request.organization_id,
        request.template,
        db=db,
        kwargs=request.kwargs,
    )
