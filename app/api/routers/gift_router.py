"""This module defines the FastAPI API endpoints for registry/gift."""


from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.schemas.gift_schemas import AddProductGift, EditProductGift
from app.database.connection import get_db
from app.services.gift_services import (
    add_product_gift,
    delete_a_gift,
    edit_product_gift,
    fetch_gift,
    gift_filter,
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


@gift_router.get("/filter-gifts")
async def filter_gifts(
    param: str = Query(default="all"),
    filter_by_date: bool
    | None = Query(
        default=False,
    ),
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    db: Session = Depends(get_db),
) -> Any:
    """Filter gifts from the Registry.

    Request:

        Method: GET

        param: `str` specific parameter (e.g all, purchased,
        available, reserved ...) for filtering gifts; default is `all`.

        filter_by_date: `bool` if true, filtering by date is enabled.

        start_date: UTC datetime string, it must be less than end date.

            If only end_date is specified, the gifts will be filtered
            from current date to the end date.

        end_date: UTC datetime string, it must be greater than start date.

        db(Session): the database session

    Response:

        Returns CustomResponse with 200 status code, message,
        and data: a List[Dict[str,Any]] containing all the gifts under
        the filter parameter.


    Exception:

        CustomException: If no gifts found or server error.
    """

    # check if filter_by_day enabled
    if filter_by_date:
        if start_date and end_date:
            response, exception = gift_filter(param, db, start_date, end_date)
        if not start_date and end_date:
            response, exception = gift_filter(param, db, None, end_date)

    if not filter_by_date:
        response, exception = gift_filter(param, db)

    if exception:
        raise exception
    return response
