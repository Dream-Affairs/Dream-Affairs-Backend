"""This module contains function that ensure a Meal is created properly."""

from typing import Any

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


def get_meal_categories(org_id: str, db: Session) -> list[dict[str, Any]]:
    """Gets all meal categories that exist for a specific organization.

    Args:
        org_id (str): The organization ID.
        db (Session): The database session.

    Returns:
        List[Dict[str, Any]]: List of dictionaries representing
        meal categories.
    """

    # Retrieve all records from the MealCategory table
    meal_categories = (
        db.query(MealCategory)
        .filter(MealCategory.organization_id == org_id)
        .all()
    )

    # Convert the SQLAlchemy objects into dictionaries
    meal_category_list = []
    for meal_category in meal_categories:
        meal_category_dict = {
            "id": meal_category.id,
            "name": meal_category.name,
            "organization_id": meal_category.organization_id,
            "organization": {
                "name": meal_category.organization.name,
                "id": meal_category.organization.id,
            },
            "meals": meal_category.meals,
        }
        meal_category_list.append(meal_category_dict)

    return meal_category_list
