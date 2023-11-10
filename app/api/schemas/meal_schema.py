from typing import Optional
from uuid import uuid4
from unittest.mock import Base
from pydantic import BaseModel, EmailStr
from datetime import datetime, date

class CreateMealCategory(BaseModel):
    name: str
    is_hidden: bool = False

class ExistingMealCategory(CreateMealCategory):
    id: uuid4
    creator_id: str
    organization_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes: True

class CreateMeal():
    name: str
    description: Optional[str] = ""
    image_url: str 
    meal_category_id: str 
    is_hidden: Optional[bool] = False
    quantity: int
