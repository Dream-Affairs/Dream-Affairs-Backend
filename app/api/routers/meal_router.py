"""This module defines the FastAPI API endpoints for meal management."""


from typing import Any, Optional

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.api.middlewares.authorization import Authorize, is_org_authorized
from app.api.responses.custom_responses import CustomResponse
from app.api.schemas.meal_schema import (
    MealCategorySchema,
    MealSchema,
    MealSortBy,
    MealSortOrder,
)
from app.database.connection import get_db
from app.services.meal_services import (
    create_mc_service,
    create_meal_service,
    create_meal_tag,
    delete_meal_service,
)
from app.services.meal_services import get_meal_categories as get_all
from app.services.meal_services import get_meal_service

BASE_URL = "/meal-management"

router = APIRouter(prefix=BASE_URL, tags=["Meal Management"])


@router.post("/meal-category")
def create_meal_category(
    meal_category: MealCategorySchema,
    auth: Authorize = Depends(is_org_authorized),
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
            org_id=auth.member.organization_id, schema=meal_category, db=db
        )

    except Exception as e:
        raise e

    return CustomResponse(
        status_code=201,
        message="Meal Category Successfully Created",
        data=new_meal_category,
    )


@router.get("/meal-category")
def get_all_meal_category(
    auth: Authorize = Depends(is_org_authorized),
    db: Session = Depends(get_db),
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
        category_list = get_all(org_id=auth.member.organization_id, db=db)

    except Exception as e:
        raise e

    return CustomResponse(
        status_code=200,
        message="All Meal Category Successfully fetched",
        data=category_list,
    )


@router.post("/meal")
def create_meal(
    meal_category_id: str,
    create_meal_schema: MealSchema,
    auth: Authorize = Depends(is_org_authorized),
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
            org_id=auth.member.organization_id,
            meal_category_id=meal_category_id,
            meal_schema=create_meal_schema,
            db=db,
        )
        if exception:
            # Raise the captured exception to handle it at a higher level
            raise exception

    except Exception as e:
        raise e

    return response


@router.get("/meal")
def get_all_meals(
    sort_by: MealSortBy,
    order: MealSortOrder,
    limit: int = 20,
    offset: int = 0,
    meal_category_id: Optional[str] = None,
    ishidden: Optional[bool] = False,
    auth: Authorize = Depends(is_org_authorized),
    db: Session = Depends(get_db),
) -> CustomResponse:
    """This is the meal endpoint to get al meal."""

    return CustomResponse(
        status_code=200,
        message="Meals retrieved successfully.",
        data=jsonable_encoder(
            get_meal_service(
                offset=offset,
                limit=limit,
                order=order,
                db=db,
                sort_by=sort_by,
                meal_category_id=meal_category_id,
                ishidden=ishidden,
                organization_id=auth.member.organization_id,
            )
        ),
    )


@router.delete("/meal/{meal_id}")
def delete_meal(meal_id: str, db: Session = Depends(get_db)) -> CustomResponse:
    """Delete a meal entry for a specified meal category.

    This endpoint deletes a meal

    Args:
        meal_id (str): The ID of the meal to be deleted.
        db (Session): The database session. (Dependency)

    Returns:
        CustomResponse: A CustomResponse containing information about the
        created meal if successful. Raises CustomException if an error occurs
        during the process.
    """

    try:
        delete_meal_service(meal_id, db=db)

    except Exception as e:
        raise e

    return CustomResponse(
        status_code=201,
        message="Meal Has Been Successfully Deleted",
    )


@router.post("/meal-tag")
def add_meal_tag(
    meal_id: str,
    tag_name: str,
    auth: Authorize = Depends(is_org_authorized),
    db: Session = Depends(get_db),
) -> Any:
    """This endpoint allows the addition of a meal tag to an existing meal. The
    meal tag data is provided in the request body as a JSON object.

    Args:
        org_id (str): The unique identifier of the organization under which the
        meal_id (str): The unique identifier of a meal.
        tag_name (str): The name of the tag to be added created.
        db (Session): The database session. (Dependency)

    Returns:
        CustomResponse: Custom response contains information about the created
            meal tag. The response includes the newly created meal
            category's details
    """
    try:
        new_meal_tag = create_meal_tag(
            org_id=auth.member.organization_id,
            meal_id=meal_id,
            tag_name=tag_name,
            db=db,
        )

    except Exception as e:
        raise e

    return CustomResponse(
        status_code=201,
        message="Meal Tag Successfully Added",
        data=jsonable_encoder(new_meal_tag),
    )
