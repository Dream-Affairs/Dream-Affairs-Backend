"""This module defines Pydantic schemas for meal management."""

from datetime import datetime
from enum import Enum
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


class MealSchema(BaseModel):  # type: ignore
    """Represents the base schema for a meal."""

    name: str
    description: Optional[str] = ""
    is_hidden: Optional[bool] = False
    image_url: str
    quantity: int = 0


class TagType(str, Enum):
    """Enum for Organization Tag."""

    DIETARY = "dietary"
    GUEST = "guest"


class OrgTagSchema(BaseModel):  # type: ignore
    """Represents the base schema for an Organization Tag."""

    id: str
    organization_id: str
    name: str
    tag_type: TagType
    description: Optional[str]


class MealTagSchema(BaseModel):  # type: ignore
    """Represents the base schema for an Meal Tag."""

    id: str
    organization_tag_id: str
    meal_id: str


class MealSortOrder(str, Enum):
    """Enum for checklist sort order."""

    ASC = "asc"
    DESC = "desc"


class MealSortBy(str, Enum):
    """Enum for checklist sort by."""

    ALL = "all"
    ORGANIZATION = "organization"
    MEAL_CATEGORY = "meal category"
