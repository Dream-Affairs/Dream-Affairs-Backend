"""This module defines the FastAPI API endpoints for meal management."""


from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.responses.custom_responses import CustomResponse
from app.api.schemas.meal_schema import MealCategorySchema, MealSchema
from app.database.connection import get_db
from app.services.meal_services import create_mc_service, create_meal_service
from app.services.meal_services import get_meal_categories as get_all

BASE_URL = "/{org_id}/meal-management"

meal_router = APIRouter(prefix=BASE_URL, tags=["Meal Management"])


@meal_router.post("/create-meal-category")
def create_meal_category(
    org_id: str,
    meal_category: MealCategorySchema,
    db: Session = Depends(get_db),
) -> Any:
    """This endpoint allows the creation of a new meal category under a
    specific organization. The meal category data is provided in the request
    body as a JSON object.

    Args:
        org_id (str): The unique identifier of the organization under which the
        meal category is being created.
        meal_category (MealCategorySchema): The schema representing the meal
        category to be created.
        db (Session): The database session. (Dependency)

    Returns:
        CustomResponse: Custom response contains information about the created
            meal category. The response includes the newly created meal
            category's details
    """
    try:
        new_meal_category = create_mc_service(
            org_id, schema=meal_category, db=db
        )

    except Exception as e:
        raise e

    return CustomResponse(
        status_code=201,
        message="Meal Category Successfully Created",
        data=new_meal_category,
    )


@meal_router.get("/get-all-meal-category")
def get_all_meal_category(
    org_id: str, db: Session = Depends(get_db)
) -> CustomResponse:
    """Retrieves all Meal Categories associated with a specific organization.

    This endpoint fetches all existing meal categories associated with the
    specified organization from the database.

    Args:
        org_id (str): The unique identifier of the logged-in organization.
        db (Session): The database session. (Dependency)

    Returns:
        CustomResponse: Custom response containing the list of all meal
        categories associated with the organization.

    Response (Success - 201):
        JSON response containing the list of all meal categories:
        - Each item represents a meal category object with the details:
            - id (str): The unique identifier of the meal category.
            - name (str): The name or title of the meal category.
            - organization_id (str): The UUID of the associated organization.
            - organization (dict): Details of the associated organization,
                including its name and ID.
            - meals (List[Meal]): The list of meals associated with category.
    """
    try:
        category_list: list[dict[str, Any]] = get_all(org_id, db)

    except Exception as e:
        raise e

    return CustomResponse(
        status_code=200,
        message="All Meal Category Successfully fetched",
        data=category_list,
    )


@meal_router.post("/create-meal")
def create_meal(
    meal_category_id: str,
    create_meal_schema: MealSchema,
    db: Session = Depends(get_db),
) -> Any:
    """Creates a new meal entry for a specified meal category.

    This endpoint facilitates the addition of a new meal entry associated with
    a specific meal category identified by 'meal_category_id'. The func takes
    in details of the meal such as name, description, quantity, image file, and
    optionally the visibility status. It internally uses 'create_meal_service'
    for handling the creation process.

    Args:
        meal_category_id (str): The ID of the meal category for the new meal.
        meal_img (UploadFile): The image file associated with the meal.
        meal_name (str): The name or title of the meal.
        meal_description (str): Description or details of the meal.
        meal_quantity (int): The quantity or serving size of the meal.
        is_hidden (Optional[bool], optional): Optional parameter indicating the
         visibility status of the meal. Defaults to False if not provided.
        db (Session): The database session. (Dependency)

    Returns:
        CustomResponse: A CustomResponse containing information about the
        created meal if successful. Raises CustomException if an error occurs
        during the process.
    """

    try:
        response, exception = create_meal_service(
            meal_category_id, create_meal_schema, db=db
        )
        if exception:
            # Raise the captured exception to handle it at a higher level
            raise exception

    except Exception as e:
        raise e

    return response
