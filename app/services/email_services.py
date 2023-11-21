"""This module is used to send an email to the recipient."""
import os
from datetime import datetime
from typing import Any, Dict, Tuple, Union

from jinja2 import Environment, FileSystemLoader
from requests import get, post, put  # type: ignore
from sqlalchemy.orm import Session

from app.api.models.email_models import EmailList, TrackEmail
from app.api.responses.custom_responses import CustomResponse
from app.core.config import settings

TEMP_FOLDER = os.path.join(os.path.abspath(settings.TEMPLATE_DIR))


class EmailService:
    """This class is used to send emails to customerss.

    It will also be used to handle mailings and newsletters.
    """

    def __init__(
        self,
        api_key: str,
        api_uri: str = settings.EMAIL_API_URI,
    ):
        """This function is used to initialize the EmailService class. It takes
        the api_key and api_uri as parameters.

        Args:
            api_key: This is the api_key of the email service.
            api_uri: This is the api_uri of the email service.

        Returns:
            This returns the response of the request.
        """
        self.api_key = api_key
        self.api_uri = api_uri

    def elastic_email_request(
        self,
        method: str,
        url: str,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """This function is used to send a request to elastimail API.

        Args:
            method: This is the method of the request.
            url: This is the url of the request.
            data: This is the data of the request.

        Returns:
            This returns the response of the request.
        """
        data["api_key"] = self.api_key
        if method == "POST":
            result = post(
                self.api_uri + url,
                data=data,
                timeout=settings.EMAIL_REQUEST_TIMEOUT,
            )
        elif method == "PUT":
            result = put(
                self.api_uri + url,
                data=data,
                timeout=settings.EMAIL_REQUEST_TIMEOUT,
            )
        elif method == "GET":
            attach = ""
            for key in data:
                attach = attach + key + "=" + data[key] + "&"
            url = url + "?" + attach[:-1]
            result = get(
                self.api_uri + url, timeout=settings.EMAIL_REQUEST_TIMEOUT
            )

        data = result.json()
        return data

    # method to send transactional emails
    def send_mail(
        self,
        subject: str,
        sender_email: str,
        sender_name: str,
        to: str,
        body_html: Union[str, None] = None,
        reply_to: Union[str, None] = None,
    ) -> Dict[str, str]:
        """This function is used to send an email to the recipient.

        Args:
            subject: This is the subject of the email.
            semder_email: This is the email address of the sender. \
                It is the email in the env file.
            sender_name: This is the name of the sender. \
                It is the name in the env file.
            to: This is the email address of the recipient.
            body_html: This is the html body of the email.
            body_text: This is the text body of the email.
            is_transactional: This is the boolean value of the email.

        Returns:
            This returns the response of the request.
        """
        mail_instance = self.elastic_email_request(
            method="POST",
            url="/email/send",
            data={
                "subject": subject,
                "from": sender_email,
                "fromName": sender_name,
                "to": to,
                "body_html": body_html,
                "replyTo": reply_to,
                "isTransactional": True,
                "trackOpens": True,
                "trackClicks": True,
                "charset": "utf-8",
            },
        )
        return mail_instance

    def get_email_status(self, message_id: str) -> Dict[str, Any]:
        """This function is used to get the status of the email.

        Args:
            message_id: This is the email id of the email.

        Returns:
            This returns the response of the request.
        """
        mail_instance = self.elastic_email_request(
            method="GET",
            url="/email/getstatus",
            data={"messageID": message_id},
        )
        return mail_instance

    def subscribe_email(self, email: str) -> Dict[str, Any]:
        """This function is used to subscribe an email.

        Args:
            email: This is the email address of the recipient.

        Returns:
            This returns the response of the request.
        """
        mail_instance = self.elastic_email_request(
            method="GET",
            url="/contact/add",
            data={"email": email},
        )
        return mail_instance

    def unsubscribe_email(self, email: str) -> Dict[str, Any]:
        """This function is used to unsubscribe an email.

        Args:
            email: This is the email address of the recipient.

        Returns:
            This returns the response of the request.
        """
        mail_instance = self.elastic_email_request(
            method="GET",
            url="/contact/remove",
            data={"email": email},
        )
        return mail_instance


Email = EmailService(settings.EMAIL_API_KEY)


def generate_html(
    template: Any,
    **kwargs: Dict[str, Any],
) -> Any:
    """This function is used to generate html from the template.

    Args:
        template: This is the template of the email.
        **kwargs: This is the dictionary of the arguments.
    """
    templates = Environment(
        loader=FileSystemLoader(TEMP_FOLDER), autoescape=True
    )
    template = templates.get_template(template)
    return template.render(**kwargs)


def formataddr(address: Tuple[str, str]) -> str:
    """This function is used to format the email address."""
    name, email_address = address
    return f"{name} <{email_address}>"


def track_email(
    message_id: str,
    db: Session,
) -> str:
    """This function is used to track the email sent to the recipient.

    Args:
        message_id: This is the message id of the email.
        db: This is the database session.

    Returns:
        This returns the message id of the email.
    """
    db_email: TrackEmail = (
        db.query(TrackEmail)
        .filter(TrackEmail.message_id == message_id)
        .first()
    )
    if db_email:
        db_email.is_read = True
        db_email.last_updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_email)
    return "Email tracked successfully"


def log_email(
    message_id: str,
    organization_id: str,
    subject: str,
    recipient: str,
    template: str,
    status: str,
    reason: str,
    db: Session,
    is_read: bool = False,
    number_of_links_in_email: int = 0,
) -> str:
    """This function is used to log the email sent to the recipient.

    Args:
        unique_id: This is the unique id of the email.
        message_id: This is the email id of the email.
        organization_id: This is the organization id of the email.
        subject: This is the subject of the email.
        recipient: This is the email address of the recipient.
        template: This is the template of the email.
        status: This is the status of the email.
        reason: This is the reason of the email.
        is_read: This is the boolean value of the email.
        sent_at: This is the date the email was sent.
        created_at: This is the date the email was created.
        updated_at: This is the date the email was updated.
        db: This is the database session.

    Returns:
        This returns the unique id of the email.
    """

    db_email = TrackEmail(
        message_id=message_id,
        organization_id=organization_id,
        subject=subject,
        recipient=recipient,
        template=template,
        status=status,
        reason=reason,
        is_read=is_read,
        number_of_links_in_email=number_of_links_in_email,
        created_at=datetime.utcnow(),
        last_updated_at=datetime.utcnow(),
    )
    try:
        db.add(db_email)
        db.commit()
        db.refresh(db_email)
    except Exception as e:
        db.rollback()
        raise e
    return "Email logged successfully"


def send_email_api(
    subject: str,
    recipient_email: str,
    organization_id: str,
    template: str,
    kwargs: Dict[str, Any],
    db: Session,
) -> str:
    """This function is used to send an email to the recipient.

    Args:
        subject: This is the subject of the email.
        recipient_email: This is the email address of the recipient.
        organization_id: This is the organization id of the email.
        template: This is the template of the email.
        kwargs: This is the dictionary of the arguments.

    Returns:
        This returns the unique id of the email.
    """

    # count number of links in email
    count = len([key for key in kwargs if "_link" in key])

    data: Dict[str, Any] = Email.send_mail(
        subject=subject,
        sender_email=settings.EMAIL_SENDER,
        sender_name=settings.EMAIL_NAME,
        to=recipient_email,
        body_html=generate_html(template, kwargs=kwargs),
    )
    if data["success"] is True:
        status = "sent"
        reason = "Email sent successfully"
    else:
        status = "failed"
        reason = data.get("error", "")

    return log_email(
        message_id=data.get("data")["messageid"],  # type: ignore
        organization_id=organization_id,
        subject=subject,
        recipient=recipient_email,
        template=template,
        status=status,
        number_of_links_in_email=count,
        reason=reason,
        db=db,
    )


def subscribe_email_service(
    email: str,
    db: Session,
) -> CustomResponse:
    """This function is used to subscribe an email.

    Args:
        email: This is the email address of the recipient.
        db: This is the database session.

    Returns:
        This returns the response of the request.
    """
    # Email.subscribe_email(email)
    db_email = EmailList(
        email=email,
        is_subscribed=True,
        date_subscribed=datetime.utcnow(),
        created_at=datetime.utcnow(),
        last_updated_at=datetime.utcnow(),
    )
    try:
        db.add(db_email)
        db.commit()
        db.refresh(db_email)
    except Exception as e:
        db.rollback()
        raise e
    return CustomResponse(
        status_code=200, message="Email subscribed successfully", data=""
    )
