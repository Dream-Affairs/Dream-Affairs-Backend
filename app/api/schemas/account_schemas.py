from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

class AccountSchema(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str
    first_name: str
    last_name: str
