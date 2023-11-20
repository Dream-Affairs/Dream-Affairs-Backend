"""This module defines the FastAPI API endpoints for registry/gift."""


from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.responses.custom_responses import CustomResponse
from app.api.schemas.gift_schemas import AddProductGift, EditProductGift
from app.database.connection import get_db
from app.services.gift_services import (
    add_product_gift,
    delete_a_gift,
    edit_product_gift,
    fetch_all_gifts,
    fetch_gift,
)

gift_router = APIRouter(prefix="/registry", tags=["Registry"])


@gift_router.post("/add-product-gift")
async def add_product(
    member_id: str,
    gift_item: AddProductGift,
    db: Session = Depends(get_db),
) -> Any:
    """Add a New product gift to Registry.

    Request:

        Method: POST

        member_id: account_id for authentication

        gift_item(AddProductGift): Request Body containing the details of the
            product gift to be added.

        db(Session): the database session

    Response: Returns CustomResponse with 201 status code and
        `data` which is a dictionary containing gift details.

    Exception:

        CustomException: If the user is not authenticated or
            a field is missing or internal server error.
    """

    response, exception = add_product_gift(gift_item, member_id, db)
    if exception:
        raise exception

    return response


@gift_router.patch("/edit-product-gift")
async def edit_product(
    gift_id: str,
    gift_item: EditProductGift,
    db: Session = Depends(get_db),
) -> Any:
    """Edit a product gift in Registry.

    Request:

        Method: PATCH

        gift_id: the ID of the gift to be edited

        gift_item(EditProductGift): Request Body containing the details of the
            product gift to be edited.

        db(Session): the database session

    Response: Returns CustomResponse with 201 status code and
        `data` which is a dictionary containing gift details.

    Exception:

        CustomException: If the user is not authenticated or
            a field is missing or internal server error.
    """
    response, exception = edit_product_gift(gift_item, gift_id, db)
    if exception:
        raise exception

    return response


@gift_router.get("/get-gift")
async def get_gift(gift_id: str, db: Session = Depends(get_db)) -> Any:
    """Get a gift from the Registry.

    Request:

        Method: GET

        gift_id: the ID of the gift to get

        db(Session): the database session

    Response: Returns CustomResponse with 200 status code and
        gift `data` which is a dictionary containing gift details.

    Exception:

        CustomException: If the user is not authenticated or
            a field is missing or internal server error.
    """

    response, exception = fetch_gift(gift_id, db)
    if exception:
        raise exception

    return response


@gift_router.delete("/delete-gift")
async def delete_gift(gift_id: str, db: Session = Depends(get_db)) -> Any:
    """Delete a gift from the Registry.

    Request:

        Method: GET

        gift_id: the ID of the gift to delete

        db(Session): the database session

    Response: Returns CustomResponse with 200 status code with a message
        if the resource was removed successfully.

    Exception:

        CustomException: If the user is not authenticated or
            gift doesn't exist or internal server error.
    """

    response, exception = delete_a_gift(gift_id, db)
    if exception:
        raise exception

    return response


@gift_router.get("/all-gifts")
async def get_all_gifts(db: Session = Depends(get_db)) -> CustomResponse:
    """Get all gifts from the Registry.

    Request:

        Method: GET

        db(Session): the database session

    Response:

        Returns CustomResponse with 200 status code, message,
        and data: a List[Dict[str,Any]] containing all the gifts.


    Exception:

        CustomException: If no gifts found or server error.
    """

    try:
        all_gifts = fetch_all_gifts(db)
    except Exception as e:
        raise e
    return CustomResponse(
        status_code=status.HTTP_200_OK,
        message="Gifts retrieved successfully",
        data=all_gifts,
    )
