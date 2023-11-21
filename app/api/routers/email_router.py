"""This module contains the email router services for the API."""

from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.api.responses.custom_responses import CustomResponse
from app.api.schemas.email_schemas import EmailSchema, EmailSubscriptionSchema
from app.database.connection import get_db
from app.services.email_services import send_email_api, subscribe_email_service

email_router = APIRouter(prefix="/email", tags=["Email"])


@email_router.post(
    "/send-email",
)
def send_email(
    request: EmailSchema,
    db: Session = Depends(get_db),
) -> CustomResponse:
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
        request.subject,
        request.recipient,
        request.organization_id,
        request.template,
        db=db,
        kwargs=request.kwargs,
    )
    return CustomResponse(
        status_code=status.HTTP_200_OK,
        message="Email sent successfully.",
        data="",
    )


@email_router.post("/subscribe")
def subscribe(
    request: EmailSubscriptionSchema, db: Session = Depends(get_db)
) -> CustomResponse:
    """This function is used to subscribe a user to the email list.

    Args:
        email: This is the email of the user.
    """
    return CustomResponse(
        status_code=status.HTTP_200_OK,
        message="Email subscription has not been fully implemented dues to \
            lack of emailing service subscription.",
        data=jsonable_encoder(subscribe_email_service(request.email, db)),
    )
