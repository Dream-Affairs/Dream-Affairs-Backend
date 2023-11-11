"""This module defines the FastAPI API endpoints for meal management."""

import fastapi
from fastapi import APIRouter
from sqlalchemy import orm

from app.api.models.meal_models import MealCategory
from app.api.responses.custom_responses import CustomResponse
from app.api.schemas.meal_schema import (
    CreateMealCategory,
    ExistingMealCategory,
)
from app.database.connection import get_db
from app.services.meal_services import get_meal_category_by_name as unique_name

BASE_URL = "/{org_id}/meal-management"

app = APIRouter(prefix=BASE_URL, tags=["Meal Management"])


@app.post("/create-meal-category", response_model=ExistingMealCategory)
def create_meal_category(
    # org_id: str,
    meal_category: CreateMealCategory,
    db: orm.Session = fastapi.Depends(get_db),
) -> CustomResponse:
    """Intro-->This endpoint allows you to create a create  a new Meal Category
    on the fly and takes in about two  paramenters. To create a Meal Category,
    you need to make  a post request to the /meal-management/create-meal-
    category endpoint.

    paramDesc-->

    reqBody-->name: This is the title of the blog post to be created.

    returnDesc-->On sucessful request, it returns

    returnBody--> the blog object with details specified below.
    """

    if unique_name(name=meal_category.name, db=db):
        raise fastapi.HTTPException(
            status_code=400, detail="Category name already exists"
        )

    category = MealCategory(**meal_category.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)

    return CustomResponse(
        status_code=201,
        message="Meal Category Successfully Created",
        data=ExistingMealCategory(**category),
    )
