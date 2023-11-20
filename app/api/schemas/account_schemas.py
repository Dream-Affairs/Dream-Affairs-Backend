"""This module defines Pydantic schemas for user accounts."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class AccountSchema(BaseModel):  # type: ignore
    """Data model for an account.

    Attributes:
        email (EmailStr): The email address of the account.
        password (str): The password of the account.
        confirm_password (str): The confirmation password of the account.
        first_name (str): The first name of the account holder.
        last_name (str): The last name of the account holder.
    """

    email: EmailStr
    password: str
    confirm_password: str
    first_name: str
    event_date: Optional[datetime]
    location: str
    partner_name: str


class TokenData(BaseModel):  # type: ignore
    """Data model for an access token.

    Attributes:
        id (Optional[str]): The ID of the token.
    """

    id: Optional[str] = None


class ForgotPasswordData(BaseModel):  # type: ignore
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
