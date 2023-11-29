"""This module contains function that ensure a Meal is created properly."""

from typing import Any
from uuid import uuid4

from fastapi import status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import InternalError
from sqlalchemy.orm import Session

from app.api.models.meal_models import Meal, MealCategory, MealTag
from app.api.models.organization_models import Organization, OrganizationTag
from app.api.responses.custom_responses import CustomException, CustomResponse
from app.api.schemas.meal_schema import MealSchema, MealTagSchema


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
    new_category = MealCategory(
        organization_id=org_id, name=schema.name, id=uuid4().hex
    )

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
            meal_tags = []
            for tag in meal.meal_tags:
                # Append meal tags to meal_tags array
                tag_dict = {
                    "type": "tag",
                    "meal_id": tag.meal_id,
                    "id": tag.id,
                    "name": tag.organization_tag.name,
                    "tag_type": tag.organization_tag.tag_type,
                    "organization_tag_id": tag.organization_tag_id,
                    # "created_at": tag.created_at,
                }
                meal_tags.append(tag_dict)

            # Append Meal to meal_list array
            meal_dict = {
                "type": "meal",
                "id": meal.id,
                "name": meal.name,
                "description": meal.description,
                "image_url": meal.image_url,
                "tags": meal_tags
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
    meal_item["id"] = uuid4().hex

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


def create_meal_tag(
    org_id: str, meal_id: str, tag_name: str, db: Session
) -> MealTagSchema:
    """Create a Meal Tag / Organization Tag."""

    # Check if the organization tag name exists else create it
    existing_tag = (
        db.query(OrganizationTag)
        .filter(OrganizationTag.name == tag_name.lower())
        .first()
    )

    if not existing_tag:
        org_tag_data = OrganizationTag(
            id=uuid4().hex,
            organization_id=org_id,
            name=tag_name.lower(),
            tag_type="dietary",
        )

        db.add(org_tag_data)
        db.commit()
        db.refresh(org_tag_data)

        tag: OrganizationTag = jsonable_encoder(org_tag_data)

        tag_id = tag["id"]

    else:
        tag = jsonable_encoder(existing_tag)

        # Check if the tag has been added to meal
        unique_meal_tag = (
            db.query(MealTag)
            .filter(
                MealTag.organization_tag_id == tag["id"],
                MealTag.meal_id == meal_id,
            )
            .first()
        )
        # print(jsonable_encoder(unique_meal_tag))
        if unique_meal_tag:
            raise CustomException(
                status_code=status.HTTP_409_CONFLICT,
                message=f"{tag_name} tag has already been added to this meal",
            )

        tag_id = tag["id"]

    # Create the meal tag with all the sufficient Ids available
    meal_tag_data = MealTag(
        id=uuid4().hex, organization_tag_id=tag_id, meal_id=meal_id
    )

    # return the tag jsonable encoder
    db.add(meal_tag_data)
    db.commit()
    db.refresh(meal_tag_data)

    return MealTagSchema(
        id=meal_tag_data.id,
        organization_tag_id=meal_tag_data.organization_tag_id,
        meal_id=meal_tag_data.meal_id,
    )
