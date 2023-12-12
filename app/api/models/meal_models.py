"""This file contains the models for the meal table."""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
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
      creator_id (str): This is the id of the creator account \
        to which the meal_category belongs.
      is_hidden (bool): This is the boolean value which \
        tells whether the meal_category is hidden or not.
      created_at (datetime): This is the date and time when the \
        meal_category was created.
      updated_at (datetime): This is the date and time when the \
        meal_category was updated.

      organization (object): This is the organization to which the \
        meal_category belongs.
      account (object): This is the account owner to which the \
        meal_category belongs.
    """

    __tablename__ = "meal_category"
    id = Column(String, primary_key=True, default=uuid4().hex)
    name = Column(String, nullable=False)
    organization_id = Column(
        String,
        ForeignKey("organization.id", ondelete="CASCADE"),
        nullable=False,
    )
    is_hidden = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    meals = relationship(
        "Meal", back_populates="meal_categories", lazy="joined"
    )
    organization = relationship(
        "Organization", back_populates="meal_categories", lazy="joined"
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
    id = Column(String, primary_key=True, default=uuid4().hex)
    name = Column(String, nullable=False)

    description = Column(
        String,
    )
    image_url = Column(
        String,
    )
    meal_category_id = Column(
        String, ForeignKey("meal_category.id"), nullable=False
    )
    organization_id = Column(
        String,
        ForeignKey("organization.id", ondelete="CASCADE"),
        nullable=False,
    )
    is_hidden = Column(Boolean, default=False)
    quantity = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    meal_categories = relationship(
        "MealCategory", back_populates="meals", lazy="joined"
    )
    meal_tags = relationship("MealTag", back_populates="meals", lazy="joined")


class MealTag(Base):  # type: ignore
    """
    MealTag:
      This class is used to create the meal_tag table.

    Attributes:
      id (str): This is the primary key of the table.
      name (str): This is the name of the meal_tag.
      organization_id (str): This is the id of the organization \
        to which the meal_tag belongs.
      is_hidden (bool): This is the boolean value which tells \
        whether the meal_tag is hidden or not.
      created_at (datetime): This is the date and time when the \
        meal_tag was created.
      updated_at (datetime): This is the date and time when the \
        meal_tag was updated.

      organization (object): This is the organization to which the \
        meal_tag belongs.
    """

    __tablename__ = "meal_tag"
    id = Column(String, primary_key=True, default=uuid4().hex)
    organization_tag_id = Column(
        String,
        ForeignKey("organization_tag.id", ondelete="CASCADE"),
        nullable=False,
    )
    meal_id = Column(
        String,
        ForeignKey("meal.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at = Column(DateTime, default=datetime.utcnow)

    meals = relationship("Meal", back_populates="meal_tags", lazy="joined")
    organization_tag = relationship(
        "OrganizationTag", back_populates="meal_tags", lazy="joined"
    )
