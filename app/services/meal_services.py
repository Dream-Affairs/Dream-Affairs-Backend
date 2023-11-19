"""This module contains function that ensure a Meal is created properly."""

from typing import Any

from fastapi import UploadFile, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import InternalError
from sqlalchemy.orm import Session

from app.api.models.meal_models import Meal, MealCategory
from app.api.models.organization_models import Organization
from app.api.responses.custom_responses import CustomException, CustomResponse

# Using the blod in gift router to store images
from app.services.blob_service import upload_image_to_azure_blob


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
    existing_name = (
        db.query(MealCategory).filter(MealCategory.name == schema.name).first()
    )

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

        # Returning a success response
        return CustomResponse(
            status_code=201,
            message="Meal Category Successfully Created",
            data=jsonable_encoder(new_category),
        )

    except InternalError as e:
        print(e)
        db.rollback()
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Failed to {new_category.name} Meal Category",
        ) from e  # Using 'from' to preserve the original exception context


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


def create_meal_service(
    meal_category_id: str,
    meal_img: UploadFile,
    meal_schema: dict[str, Any],
    db: Session,
) -> Any:
    """Creates a new meal tied to a specific meal category.

    This function checks if the meal category exists. If not, it reports an
    error. Then, it uploads an image, prepares meal details, and creates a
    new meal. If everything goes well, it confirms the addition of the meal.

    Args:
        meal_category_id (str): ID of the meal's category.
        meal_img (UploadFile): Image file for the meal.
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

    # upload a blob and retrieve the url
    image_url = upload_image_to_azure_blob(
        meal_category_id, meal_img, meal_schema["name"]
    )

    # meal_schema = meal.model_dump()
    meal_schema["meal_category_id"] = meal_category_id
    meal_schema["image_url"] = image_url

    # Compiling attributes to make up a meal model
    new_meal = Meal(**meal_schema)

    try:
        db.add(new_meal)
        db.commit()
        db.refresh(new_meal)

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
