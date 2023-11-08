"""
This module defines Pydantic schemas for user accounts.
"""

from pydantic import BaseModel, EmailStr


class AccountSchema(BaseModel):
    """
    Represents the schema for an account.
    """

    email: EmailStr
    password: str
    confirm_password: str
    first_name: str
    last_name: str
