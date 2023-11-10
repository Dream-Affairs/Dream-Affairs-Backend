"""This module defines Pydantic schemas for user accounts."""

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
    last_name: str


class TokenData(BaseModel):  # type: ignore
    """Data model for an access token.

    Attributes:
        id (Optional[str]): The ID of the token.
    """

    id: Optional[str] = None
