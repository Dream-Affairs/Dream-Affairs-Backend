"""This module contains function that ensure a Meal is created properly."""

from typing import Any

from fastapi import status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import InternalError
from sqlalchemy.orm import Session

from app.api.models.meal_models import Meal, MealCategory
from app.api.models.organization_models import Organization
from app.api.responses.custom_responses import CustomException, CustomResponse
from app.api.schemas.meal_schema import MealSchema


def create_mc_service(org_id: str, schema: MealCategory, db: Session) -> Any:
    """Creates a new meal category for a specific organization.

    This function ensures the validity of the organization ID and checks if
    the given name for the meal category is already in use. If both conditions
    are met, it creates a new meal category associated with the organization.

    Args:
        org_id (str): ID of the organization for the new meal category.
        schema (str): Schema containing details of the new meal category.
        db (Session): Database session.

    Returns:
       Union[CustomResponse, CustomException]: CustomResponse if meal category
       creation succeeds, CustomException for errors.
    """
    # Checking if the organization with the given ID exists
    valid_organization = (
        db.query(Organization).filter(Organization.id == org_id).first()
    )

    if not valid_organization:
        raise CustomException(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Invalid Organization ID",
        )

    # Checking if the meal category name already exists
    existing_name = False

    for category in valid_organization.meal_categories:
        if category.name == schema.name:
            existing_name = True
            break

    if existing_name:
        raise CustomException(
            status_code=status.HTTP_409_CONFLICT,
            message="This name has already been used",
        )

    # Creating a new meal category
    new_category = MealCategory(organization_id=org_id, name=schema.name)

    try:
        db.add(new_category)
        db.commit()
        db.refresh(new_category)
    except InternalError as e:
        print(e)
        db.rollback()
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Failed to {new_category.name} Meal Category",
        ) from e  # Using 'from' to preserve the original exception context

    # Returning a success response
    return jsonable_encoder(new_category)


def get_meal_categories(org_id: str, db: Session) -> list[dict[str, Any]]:
    """Gets all meal categories that exist for a specific organization.

    Args:
        org_id (str): The organization ID.
        db (Session): The database session.

    Returns:
        List[Dict[str, Any]]: List of dictionaries representing
        meal categories.
    """

    # Checking if the organization with the given ID exists
    valid_organization = (
        db.query(Organization).filter(Organization.id == org_id).first()
    )

    if not valid_organization:
        raise CustomException(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Invalid Organization ID",
        )

    # Retrieve all records from the MealCategory table
    meal_categories = (
        db.query(MealCategory)
        .filter(MealCategory.organization_id == org_id)
        .all()
    )

    # Convert the SQLAlchemy objects into dictionaries
    meal_category_list = []
    for meal_category in meal_categories:
        # Serialize meals into dictionaries before push to meal_category_dict
        meal_list = []
        for meal in meal_category.meals:
            meal_dict = {
                "type": "meal",
                "id": meal.id,
                "name": meal.name,
                "description": meal.description,
                "image_url": meal.image_url,
                "tags": meal.meal_tags
                # Add other relevant fields from Meal model here
            }
            meal_list.append(meal_dict)

        meal_category_dict = {
            "id": meal_category.id,
            "name": meal_category.name,
            "organization_id": meal_category.organization_id,
            "organization": {
                "name": meal_category.organization.name,
                "id": meal_category.organization.id,
            },
            "meals": meal_list,  # Serialize meals as dictionaries
        }
        meal_category_list.append(meal_category_dict)

    return meal_category_list


def create_meal_service(
    meal_category_id: str,
    meal_schema: MealSchema,
    db: Session,
) -> Any:
    """Creates a new meal tied to a specific meal category.

    This function checks if the meal category exists. If not, it reports an
    error. Then creates a new meal. If everything goes well, it confirms the
    addition of the meal.

    Args:
        meal_category_id (str): ID of the meal's category.
        meal_schema (MealSchema): Details of the new meal.
        db (Session): Database session.

    Returns:
        Tuple[Optional[CustomResponse], Optional[CustomException]]:
        CustomResponse if meal creation succeeds, CustomException for errors.
    """

    # Check if meal category exists
    valid_meal_category = (
        db.query(MealCategory)
        .filter(MealCategory.id == meal_category_id)
        .first()
    )

    # if meal category doesn't exist throw 404 Not Found
    if not valid_meal_category:
        raise CustomException(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Meal Category not found",
        )

    meal_item = meal_schema.model_dump()
    meal_item["meal_category_id"] = meal_category_id

    # Compiling attributes to make up a meal model
    new_meal = Meal(**meal_item)

    try:
        db.add(new_meal)
        db.commit()
        db.refresh(new_meal)

        # Return response message or None
        response = CustomResponse(
            status_code=status.HTTP_201_CREATED,
            message=f"{new_meal.name} meal Successfully added",
            data=jsonable_encoder(new_meal),
        )
        return response, None

    except InternalError as e:
        print(e)
        db.rollback()
        exception = CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Failed to {new_meal.name} Meal Category",
        )

        return None, exception
