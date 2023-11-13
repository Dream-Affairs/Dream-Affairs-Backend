"""This module contains function that ensure a Meal is created properly."""

from sqlalchemy.orm import Session

from app.api.models.meal_models import MealCategory
from app.api.responses.custom_responses import CustomResponse


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


def get_meal_categories(org_id: str, db: Session) -> CustomResponse:
    """Gets all meal categories that exist for a specific organization.

    Args:
        org_id (str): The organization ID.
        db (Session): The database session.

    Returns:
        list: List of dictionaries representing meal categories.
    """

    # Retrieve all records from the MealCategory table
    meal_categories = (
        db.query(MealCategory)
        .filter(MealCategory.organization_id == org_id)
        .all()
    )

    # # Convert the result to a list of dictionaries
    meal_category_list = [
        meal_category.__dict__ for meal_category in meal_categories
    ]

    return CustomResponse(
        status_code=201,
        essage="Fetch all meal category",
        data=meal_category_list,
    )
