from datetime import datetime
from uuid import uuid4
from fastapi import APIRouter
from typing import List
import fastapi as fastapi
import sqlalchemy.orm as orm

from app.api.schemas import meal_schema as schema
from app.api.models import meal_models as model

from app.database.connection import get_db

BASE_URL = "/{org_id}/meal-management"

app = APIRouter(prefix=BASE_URL, tags=["Meal Management"])

@app.post("/create-meal-category", response_model=schema.ExistingMealCategory)
def create_meal_category(
    org_id: str,
    meal_category: schema.CreateMealCategory, 
    db: orm.Session = fastapi.Depends(get_db)
    ):
    
    """intro-->This endpoint allows you to create a create a new Meal Category on the fly and takes in about two paramenters. To create a Meal Category, you need to make a post request to the /meal-management/create-meal-category endpoint

    paramDesc-->

        reqBody-->name: This is the title of the blog post to be created.

    returnDesc-->On sucessful request, it returns

        returnBody--> the blog object with details specified below.
    """
    
    if model.get_mealCategory_by_name(name=meal_category.name, db=db):
        raise fastapi.HTTPException(status_code=400, detail="Category name already exists")
    
    category = model.MealCategory(**meal_category.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)

    return schema.ExistingMealCategory(category)