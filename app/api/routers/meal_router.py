"""This module defines the FastAPI API endpoints for meal management."""

import fastapi
from fastapi import APIRouter
from sqlalchemy import orm

from app.api.models.meal_models import MealCategory as model
from app.api.responses.custom_responses import CustomException, CustomResponse
from app.api.schemas.meal_schema import (
    CreateMealCategory,
    ExistingMealCategory,
)
from app.database.connection import get_db
from app.services.meal_services import get_meal_categories as get_all
from app.services.meal_services import get_meal_category_by_name as unique_name

BASE_URL = "/{org_id}/meal-management"

meal_router = APIRouter(prefix=BASE_URL)


@meal_router.post("/create-meal-category", response_model=ExistingMealCategory)
def create_meal_category(
    org_id: str,
    meal_category: CreateMealCategory,
    db: orm.Session = fastapi.Depends(get_db),
) -> CustomResponse:
    """Intro--> This endpoint allows you to create a create  a new Meal
    Category on the fly and takes in about two  paramenters. To create a Meal
    Category, you need to make  a post request to the /meal-management/create-
    meal- category endpoint.

    paramDesc-->org_id: Organization ID of the organization logged into.
                CreateMealCategory: Schema for incoming Data
                db: Database Session

    reqBody-->name: This is the title of the blog post to be created.

    returnDesc-->On sucessful request, it returns

    returnBody--> the blog object with details specified below.
    """
    if unique_name(name=meal_category.name, db=db):
        raise CustomException(
            status_code=400, detail="Category name already exists"
        )

    category = model(organization_id=org_id, **meal_category.model_dump())
    # category = model(**meal_category.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)

    return CustomResponse(
        status_code=201,
        message="Meal Category Successfully Created",
        data=ExistingMealCategory(**category),
    )


@meal_router.get("/get-all-meal-category")
def get_all_meal_category(
    org_id: str, db: orm.Session = fastapi.Depends(get_db)
) -> CustomResponse:
    """Intro--> This endpoint allows you to get all Meal Category in the
    database. To get all Meal Categories, you need to make a get request to the
    /meal-management/get_all endpoint.

    paramDesc-->org_id: Organization ID of the organization logged into.
                CreateMealCategory: Schema for incoming Data
                db: Database Session

    returnDesc-->On sucessful request, it returns list of all categories

    returnBody--> the meal category object with details specified below.
    """

    return get_all(org_id, db)
