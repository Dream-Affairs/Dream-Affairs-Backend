"""This module contains function that ensure a Meal is created properly."""

from typing import Any, Optional
from uuid import uuid4

from fastapi import status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import InternalError
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import desc

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
        meal_category_dict = {
            "id": meal_category.id,
            "name": meal_category.name,
            "created at": meal_category.created_at.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        }
        meal_category_list.append(meal_category_dict)

    return meal_category_list


def fetch_meal_category_by_id(
    meal_category_id: str, db: Session
) -> MealCategory:
    """Gets a meal categories that exist from the ID provided."""

    # Retrieve all records from the MealCategory table
    meal_category = (
        db.query(MealCategory)
        .filter(MealCategory.id == meal_category_id)
        .first()
    )

    if not meal_category:
        raise CustomException(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Meal not found",
        )

    return meal_category


def create_meal_service(
    org_id: str,
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
    meal_item["organization_id"] = org_id

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


def get_meal_service(
    offset: int,
    limit: int,
    order: str,
    db: Session,
    sort_by: str,
    organization_id: str,
    meal_category_id: Optional[str] = None,
    ishidden: Optional[bool] = False,
) -> Any:
    """Get all meals in the database."""
    if sort_by == "meal category":
        if meal_category_id is None:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND,
                message="Please parse in a Meal category ID",
            )
        query = db.query(Meal).filter(
            Meal.meal_category_id == meal_category_id,
            Meal.is_hidden == ishidden,
        )

    if sort_by == "organization":
        query = db.query(Meal).filter(
            Meal.organization_id == organization_id, Meal.is_hidden == ishidden
        )

    if sort_by == "all":
        query = db.query(Meal).filter(Meal.is_hidden == ishidden)

    # Order the query
    if order == "desc":
        query = query.order_by(desc(Meal.created_at))
    else:
        query = query.order_by(Meal.created_at)
    # Calculate total count before applying limit and offset
    total = query.count()

    # Initialize next_url and previous_url
    next_url = None
    previous_url = None

    # Apply limit and offset
    if total > 1:
        query = query.offset(offset).limit(limit)
        next_offset = offset + limit
        if next_offset < total:
            next_url = f"/{organization_id}/meal-management/meal?\
meal_category_id={meal_category_id}&ishidden={ishidden}&limit=\
{limit}&offset={next_offset}"

        if offset - limit >= 0:
            previous_url = f"/{organization_id}/meal-management/meal?\
meal_category_id={meal_category_id}&ishidden={ishidden}&limit=\
{limit}&offset={offset - limit}"

    meals = query.all()

    return {
        "total": total,
        "next_page_url": next_url,
        "previous_page_url": previous_url,
        "Meals": [
            {
                "id": item.id,
                "meal_categgory_id": item.meal_category_id,
                "name": item.name,
                "description": item.description,
                "image_url": item.image_url,
                "quantity": item.quantity,
                "is_hidden": item.is_hidden,
                "created_by": item.created_at,
            }
            for item in meals
        ],
    }


def fetch_meal_by_id(meal_id: str, db: Session) -> Meal:
    """Gets a meal categories that exist from the ID provided."""

    meal = db.query(Meal).filter(Meal.id == meal_id).first()

    if not meal:
        raise CustomException(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Meal not found",
        )

    return meal


def delete_meal_service(meal_id: str, db: Session) -> bool:
    """Delete a meal from the meal database."""

    # check if the meal exists
    existing_meal = db.query(Meal).filter(Meal.id == meal_id).first()

    if existing_meal:
        db.delete(existing_meal)
        db.commit()
    else:
        raise CustomException(
            status_code=status.HTTP_404_NOT_FOUND,
            message="The meal_id provided doesn't exist",
        )

    return True


def hide_meal_service(meal_id: str, db: Session) -> bool:
    """Hides a meal from the meal database."""

    # check if the meal exists
    existing_meal = db.query(Meal).filter(Meal.id == meal_id).first()

    if existing_meal:
        existing_meal.is_hidden = True
        db.commit()
    else:
        raise CustomException(
            status_code=status.HTTP_404_NOT_FOUND,
            message="The meal_id provided doesn't exist",
        )

    return True


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
        tag: OrganizationTag = create_org_tag(org_id, tag_name, "dietary", db)

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
        name=tag["name"],
        organization_tag_id=meal_tag_data.organization_tag_id,
        meal_id=meal_tag_data.meal_id,
        created_at=tag["created_at"],
    )


def create_org_tag(
    org_id: int, tag_name: str, tag_type: str, db: Session
) -> OrganizationTag:
    """This Endpoint is creates an organization tag."""

    org_tag_data = OrganizationTag(
        id=uuid4().hex,
        organization_id=org_id,
        name=tag_name.lower(),
        tag_type=tag_type,
    )

    db.add(org_tag_data)
    db.commit()
    db.refresh(org_tag_data)

    tag: OrganizationTag = jsonable_encoder(org_tag_data)

    return tag


def get_all_meal_tag_service(
    meal_id: str,
    db: Session,
) -> Any:
    """Get all meals in the database."""

    existing_meal = db.query(Meal).filter(Meal.id == meal_id).first()

    if not existing_meal:
        raise CustomException(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Meal not found",
        )

    tags = db.query(MealTag).filter(MealTag.meal_id == meal_id).all()

    tag_list: list[MealTagSchema] = []

    for tag in tags:
        query = (
            db.query(OrganizationTag)
            .filter_by(id=tag.organization_tag_id)
            .first()
        )

        if query:
            # Create an instance of MealTagSchema and append it to tag_list
            meal_tag_schema = MealTagSchema(
                id=tag.id,
                name=query.name,
                organization_tag_id=tag.organization_tag_id,
                meal_id=tag.meal_id,
                created_at=query.created_at,
            )
            tag_list.append(meal_tag_schema)

    total = len(tag_list)

    return {"total": total, "tags": tag_list}


def fetch_meal_tag_by_id(meal_tag_id: str, db: Session) -> MealTag:
    """Gets a meal tag with the ID provided."""

    meal_tag = db.query(MealTag).filter(MealTag.id == meal_tag_id).first()

    if not meal_tag:
        raise CustomException(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Meal Tag not found",
        )

    tag = (
        db.query(OrganizationTag)
        .filter(OrganizationTag.id == meal_tag.organization_tag_id)
        .first()
    )

    return tag.name, meal_tag


def delete_meal_tag_service(meal_tag_id: str, db: Session) -> bool:
    """Delete a meal from the meal database."""

    # check if the meal exists
    existing_tag: MealTag = (
        db.query(MealTag).filter(MealTag.id == meal_tag_id).first()
    )

    if not existing_tag:
        raise CustomException(
            status_code=status.HTTP_404_NOT_FOUND,
            message="The meal_tag_id provided doesn't exist",
        )

    db.delete(existing_tag)
    db.commit()

    return True
