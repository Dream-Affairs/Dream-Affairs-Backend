"""This file contains the models for the meal table."""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship

from app.database.connection import Base


class MealCategory(Base):  # type: ignore
    """
    MealCategory:
      This class is used to create the meal_category table.

    Attributes:
      id (str): This is the primary key of the table.
      name (str): This is the name of the meal_category.
      organization_id (str): This is the id of the organization \
        to which the meal_category belongs.
      is_hidden (bool): This is the boolean value which \
        tells whether the meal_category is hidden or not.
      created_at (datetime): This is the date and time when the \
        meal_category was created.
      updated_at (datetime): This is the date and time when the \
        meal_category was updated.

      organization (object): This is the organization to which the \
        meal_category belongs.
    """

    __tablename__ = "meal_category"
    id = Column(String, primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    organization_id = Column(
        String, ForeignKey("organization.id"), nullable=False
    )
    is_hidden = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship(
        "Organization", backref="meal_category", lazy=True
    )


class Meal(Base):  # type: ignore
    """
    Meal:
      This class is used to create the meal table.

    Attributes:
      id (str): This is the primary key of the table.
      name (str): This is the name of the meal.
      description (str): This is the description of the meal.
      image_url (str): This is the image_url of the meal.
      meal_category_id (str): This is the id of the meal_category \
        to which the meal belongs.
      is_hidden (bool): This is the boolean value which tells \
        whether the meal is hidden or not.
      quantity (int): This is the quantity of the meal.
      dieatary_preference (list): This is the list of \
        dieatary_preference of the meal.
      created_at (datetime): This is the date and time when the \
        meal was created.
      updated_at (datetime): This is the date and time when the \
        meal was updated.

      meal_category (object): This is the meal_category to which the\
         meal belongs.
    """

    __tablename__ = "meal"
    id = Column(String, primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    image_url = Column(String, nullable=False)
    meal_category_id = Column(
        String, ForeignKey("meal_category.id"), nullable=False
    )
    is_hidden = Column(Boolean, default=False)
    quantity = Column(Integer, nullable=False)
    dieatary_preference = Column(ARRAY(String), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
