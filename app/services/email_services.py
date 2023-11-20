"""This module is used to send an email to the recipient."""
import json
import os
from datetime import datetime
from typing import Any, Dict, Tuple, Union
from uuid import uuid4

from jinja2 import Environment, FileSystemLoader
from requests import get, post, put  # type: ignore
from sqlalchemy.orm import Session

from app.api.models.email_models import TrackEmail
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
        semder_email: str,
        sender_name: str,
        to: str,
        body_html: Union[str, None] = None,
        body_text: Union[str, None] = None,
    ) -> Dict[str, Any]:
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
                "from": semder_email,
                "fromName": sender_name,
                "to": to,
                "body_html": body_html,
                "body_text": body_text,
            },
        )
        return mail_instance

    def log_email(
        self,
        unique_id: str,
        email_id: str,
        organization_id: str,
        subject: str,
        recipient: str,
        template: str,
        status: str,
        reason: str,
        db: Session,
        is_read: bool = False,
    ) -> str:
        """This function is used to log the email sent to the recipient.

        Args:
            unique_id: This is the unique id of the email.
            email_id: This is the email id of the email.
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
            email_id=email_id,
            organization_id=organization_id,
            subject=subject,
            recipient=recipient,
            template=template,
            status=status,
            reason=reason,
            is_read=is_read,
            created_at=datetime.utcnow(),
            last_updated_at=datetime.utcnow(),
            unique_id=unique_id,
        )
        try:
            db.add(db_email)
            db.commit()
            db.refresh(db_email)
        except Exception as e:
            db.rollback()
            raise e
        return unique_id

    def track_email(
        self,
        unique_id: str,
        db: Session,
    ) -> str:
        """This function is used to track the email sent to the recipient.

        Args:
            unique_id: This is the unique id of the email.
            db: This is the database session.

        Returns:
            This returns the unique id of the email.
        """
        db_email: TrackEmail = (
            db.query(TrackEmail)
            .filter(TrackEmail.unique_id == unique_id)
            .first()
        )
        if db_email:
            db_email.is_read = True
            db_email.last_updated_at = datetime.utcnow()
            db.commit()
            db.refresh(db_email)
        return "Email tracked successfully"


email = EmailService(settings.EMAIL_API_KEY)


def send_company_email_api(
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
    data = email.send_mail(
        subject=subject,
        semder_email=settings.EMAIL_SENDER,
        sender_name=settings.EMAIL_NAME,
        to=recipient_email,
        body_html=generate_html(template, kwargs=kwargs),
    )
    if data["success"] is True:
        status = "sent"
    else:
        status = "failed"

    return email.log_email(
        email_id=data.get("data")["messageid"],  # type: ignore
        organization_id=organization_id,
        subject=subject,
        recipient=recipient_email,
        template=template,
        status=status,
        unique_id=uuid4().hex,
        reason=json.dumps(data),
        db=db,
    )


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
