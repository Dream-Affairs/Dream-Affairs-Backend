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
    event_date: Optional[datetime] | None = None
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


class AccountAuthorized(BaseModel):  # type: ignore
    """Data model for an authorized account.

    Attributes:
        id (str): The ID of the account.
        first_name (str): The first name of the account.
        last_name (str): The last name of the account.
        email (EmailStr): The email address of the account.
        phone_number (str): The phone number of the account.
        is_verified (bool): Whether the account is verified.
        is_2fa_enabled (bool): Whether 2FA is enabled for the account.
        is_deleted (bool): Whether the account is deleted.
    """

    id: str
    first_name: str
    last_name: str = ""
    email: EmailStr
    is_verified: bool


class AccountLoginResponse(VerifyAccountTokenData):  # type: ignore
    """Data model for an account response.

    Attributes:
        id (str): The ID of the account.
        first_name (str): The first name of the account.
        last_name (str): The last name of the account.
        email (EmailStr): The email address of the account.
        phone_number (str): The phone number of the account.
        is_verified (bool): Whether the account is verified.
        is_2fa_enabled (bool): Whether 2FA is enabled for the account.
        is_deleted (bool): Whether the account is deleted.
    """

    is_verified: bool
    is_2fa_enabled: bool
