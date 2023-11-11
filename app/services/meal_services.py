"""This module contains function that ensure a Meal is created properly."""

from sqlalchemy.orm import Session

from app.api.models.meal_models import MealCategory


def get_meal_category_by_name(name: str, db: Session) -> bool:
    """Check if a meal category with the given name exists.

    Args:
        name (str): The name of the meal category.
        db (orm.Session): The database session.

    Returns:
        bool: If the meal category exists, return True
        bool: otherwise, returns False.
    """
    value = db.query(MealCategory).filter(MealCategory.name == name).first()

    return bool(value)
