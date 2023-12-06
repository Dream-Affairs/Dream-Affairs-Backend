"""This module defines Pydantic schemas for user accounts."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class AccountBase(BaseModel):  # type: ignore
    """Data model for an account.

    Attributes:
        email (EmailStr): The email address of the account.
    """

    email: EmailStr


class AccountLogin(AccountBase):  # type: ignore
    """Data model for an account login."""

    password: str
    provider: str = "local"


class AccountSignup(AccountLogin):  # type: ignore
    """Data model for an account signup."""

    confirm_password: str
    first_name: str
    event_date: Optional[datetime] = None
    location: str
    partner_name: str


class TokenData(BaseModel):  # type: ignore
    """Data model for an access token.

    Attributes:
        id (Optional[str]): The ID of the token.
    """

    id: Optional[str] = None


class ForgotPasswordData(AccountBase):  # type: ignore
    """Represents the data required for the forgot password functionality.

    Attributes:
        email (EmailStr): The email address of the user.
    """

    email: EmailStr


class VerifyAccountTokenData(BaseModel):  # type: ignore
    """Data model for verifiying an account.

    Attributes:
        token (str): The account verification token.
    """

    token: str


class ResetPasswordData(BaseModel):  # type: ignore
    """Data model for resetting a password.

    Attributes:
        token (str): The reset password token.
        password (str): The new password.
        confirm_password (str): Confirmation of the new password.
    """

    token: str
    password: str
    confirm_password: str
