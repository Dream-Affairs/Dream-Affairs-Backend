"""Schemas for email service."""
from typing import Any, Dict

from pydantic import BaseModel, EmailStr


class EmailSchema(BaseModel):  # type: ignore
    """This class is used to validate the data passed to the email service."""

    subject: str
    recipient: EmailStr
    template: str
    kwargs: Dict[str, Any]
    organization_id: str


class TrackEmailSchema(BaseModel):  # type: ignore
    """This class is used to validate the data passed to the email service."""

    unique_id: str


class EmailSubscriptionSchema(BaseModel):  # type: ignore
    """This class is used to validate the data passed to the email service."""

    email: EmailStr
