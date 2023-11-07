from pydantic import BaseModel, Field, EmailStr
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
        orm_mode = True
