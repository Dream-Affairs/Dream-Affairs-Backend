"""This module defines Pydantic schemas for meal management."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MealCategorySchema(BaseModel):  # type: ignore
    """Represents the base schema for a male category."""

    name: str


class MealCategoryResponse(MealCategorySchema):
    """Represents the schema for a created Meal Category."""

    id: str
    is_hidden: bool = False
    creator_id: str
    organization_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        """Repersents the config model for this Schema
        Aim:
            Specify how I want my schema to react with the data I pass
        orm_mode:
            Converts sqlalchemy models to dictionarits for smooth passin"""

        from_attributes = True


class MealSchema:
    """Represents the base schema for a meal."""

    name: str
    description: Optional[str] = ""
    image_url: str
    meal_category_id: str
    is_hidden: Optional[bool] = False
    quantity: int
