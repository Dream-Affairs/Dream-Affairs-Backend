"""This module defines the FastAPI API endpoints for registry/gift."""


from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.middlewares.authorization import Authorize, is_org_authorized
from app.api.responses.custom_responses import CustomResponse
from app.api.schemas.gift_schemas import (
    AddCashGift,
    AddProductGift,
    EditProductGift,
    FilterGiftSchema,
)
from app.database.connection import get_db
from app.services.gift_services import (
    add_cash_gift,
    add_product_gift_,
    delete_a_gift,
    edit_product_gift_,
    fetch_gift,
    gifts_filter,
)

router = APIRouter(prefix="/gift", tags=["Registry"])


@router.post("/product")
async def add_product_gift(
    gift_item: AddProductGift,
    db: Session = Depends(get_db),
    auth: Authorize = Depends(is_org_authorized),
) -> Any:
    """Add a New product gift to Registry.

    Request:

        Method: POST;
        gift_item(AddProductGift): Request Body containing the details of the
            product gift to be added.
    Response: Returns CustomResponse with 201 status code and
        `data` which is a dictionary containing gift details.
    Exception:
        CustomException: If the user is not authenticated or
            a field is missing or internal server error.
    """

    response, exception = add_product_gift_(
        gift_item, auth.member.organization_id, db
    )
    if exception:
        raise exception

    return response


@router.patch("/product")
async def edit_product_gift(
    gift_id: str,
    gift_item: EditProductGift,
    db: Session = Depends(get_db),
    auth: Authorize = Depends(  # pylint: disable=unused-argument
        is_org_authorized
    ),
) -> Any:
    """Edit a product gift in Registry.

    Request:
        Method: PATCH;
        gift_id: the ID of the gift to be edited;
        gift_item(EditProductGift): Request Body containing the details of the
            product gift to be edited.
    Response: Returns CustomResponse with 201 status code and
        `data` which is a dictionary containing gift details.;
    Exception:
        CustomException: If the user is not authenticated or
            a field is missing or internal server error.
    """
    response, exception = edit_product_gift_(gift_item, gift_id, db)
    if exception:
        raise exception

    return response


@router.get("")
async def get_gift(
    gift_id: str,
    db: Session = Depends(get_db),
    auth: Authorize = Depends(  # pylint: disable=unused-argument
        is_org_authorized
    ),
) -> Any:
    """Get a gift from the Registry.

    Request:
        Method: GET;
        gift_id: the ID of the gift to get
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


@router.delete("/{gift_id}")
async def delete_gift(
    gift_id: str,
    db: Session = Depends(get_db),
    auth: Authorize = Depends(  # pylint: disable=unused-argument
        is_org_authorized
    ),
) -> Any:
    """Delete a gift from the Registry.

    Request:
        Method: GET;
        gift_id: the ID of the gift to delete
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


@router.post("")
async def get_all_gifts(
    request: FilterGiftSchema,
    db: Session = Depends(get_db),
    auth: Authorize = Depends(  # pylint: disable=unused-argument
        is_org_authorized
    ),
) -> Any:
    """Get gifts from the Registry.

    Request:
        Method: POST;
        request (Schema):
            org_id : `str` the id of the organization;
            filter_parameter: `str` specific parameter (e.g all, purchased,
            available, reserved ...) to use for filtering gifts; default
            is `all`.;
            filter_by_date: `bool` if true, filtering by date is enabled,
            default is `false`.;
            start_date: UTC datetime string, it must be less than end date.
                If only end_date is specified, the gifts will be filtered
                by dates <= end_date.;
            end_date: UTC datetime string, it must be greater than start date.;
    Response:
        Returns CustomResponse with 200 status code, message,
        and data: a List[Dict[str,Any]] containing all the gifts under
        the filter parameter.;
    Exception:
        CustomException: If no gifts found or server error.;
    """

    response, exception = gifts_filter(request, db)

    if exception:
        raise exception
    return response


@router.post("/cash")
async def add_cash_funds_gift(
    request: AddCashGift,
    db: Session = Depends(get_db),
    auth: Authorize = Depends(is_org_authorized),
) -> CustomResponse:
    """Add a cash funds gift to organization registry.

    Args:
        request(AddCashGift).
    Raises:
        CustomException: If something goes wrong
    Returns:
        CustomResponse: Added gift details
    """
    try:
        added_gift_details = add_cash_gift(
            auth.member.organization_id,
            request,
            db,
        )
    except Exception as e:
        raise e

    return added_gift_details
