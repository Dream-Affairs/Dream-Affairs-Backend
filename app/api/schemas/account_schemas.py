from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime


class AccountSchema(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str
    first_name: str
    last_name: str


class AccountResponse(BaseModel):
    id: str
    email: EmailStr
    first_name: str
    last_name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None
