"""This module defines the FastAPI API endpoints for meal management."""


from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.models.meal_models import MealCategory as model
from app.api.responses.custom_responses import CustomException, CustomResponse
from app.api.schemas.meal_schema import MealCategorySchema
from app.database.connection import get_db
from app.services.meal_services import get_meal_categories as get_all
from app.services.meal_services import get_meal_category_by_name as unique_name

BASE_URL = "/{org_id}/meal-management"

meal_router = APIRouter(prefix=BASE_URL, tags=["Meal Management"])


@meal_router.post("/create-meal-category")
def create_meal_category(
    org_id: str,
    meal_category: MealCategorySchema,
    db: Session = Depends(get_db),
) -> CustomResponse:
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

    if unique_name(name=meal_category.name, db=db):
        raise CustomException(
            status_code=400, detail="Category name already exists"
        )

    category = model(organization_id=org_id, **meal_category.model_dump())

    db.add(category)
    db.commit()
    db.refresh(category)

    return CustomResponse(
        status_code=201,
        message="Meal Category Successfully Created",
        data={
            "id": category.id,
            "name": category.name,
            "organization_id": category.organization_id,
            "organization": {
                "name": category.organization.name,
                "id": category.organization.id,
            },
            "meals": category.meals,
        },
    )


@meal_router.get("/get-all-meal-category")
def get_all_meal_category(
    org_id: str, db: Session = Depends(get_db)
) -> CustomResponse:
    """Retrieve all Meal Categories.

    This endpoint fetches all existing meal categories associated with the
    specified organization from the database. To retrieve all meal categories,
    send a GET request to the /meal-management/get_all endpoint.

    Args:
        org_id (str): The unique identifier of the organization logged in.
        db (Session): The database session. (Dependency)

    Returns:
        CustomResponse: Custom response containing the list of all meal
            categories associated with the organization.

    Response (Success - 200):
        JSON response containing the list of all meal categories:
        - Each item in the list represents a meal category object with
            the following details:
            - id (str): The unique identifier of the meal category.
            - name (str): The name or title of the meal category.
            - organization_id (str): The uuid of the organization associated
                with the meal category.
            - organization (dict): Details of the associated organization,
                including its name and ID.
            - meals (List[Meal]): The list of meals associated with the
                category.
    """

    category_list = get_all(org_id, db)

    return CustomResponse(
        status_code=201,
        message="All Meal Category Successfully fetched",
        data=category_list,
    )
