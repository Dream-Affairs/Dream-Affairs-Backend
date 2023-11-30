"""This module defines the FastAPI API endpoints for registry/gift."""


from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.responses.custom_responses import CustomResponse
from app.api.schemas.gift_schemas import (
    AddProductGift,
    BankSchema,
    EditProductGift,
    FilterGiftSchema,
    WalletSchema,
)
from app.database.connection import get_db
from app.services.gift_services import (
    add_bank_account,
    add_product_gift_,
    add_wallet,
    delete_a_gift,
    edit_product_gift_,
    fetch_gift,
    gifts_filter,
)

gift_router = APIRouter(prefix="/registry", tags=["Registry"])


@gift_router.post("/add-product-gift")
async def add_product_gift(
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

    response, exception = add_product_gift_(gift_item, member_id, db)
    if exception:
        raise exception

    return response


@gift_router.patch("/edit-product-gift")
async def edit_product_gift(
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
    response, exception = edit_product_gift_(gift_item, gift_id, db)
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


@gift_router.post("/get-gifts")
async def get_all_gifts(
    request: FilterGiftSchema,
    db: Session = Depends(get_db),
) -> Any:
    """Get gifts from the Registry.

    Request:

        Method: POST

        request (Schema):

            org_id : `str` the id of the organization

            filter_parameter: `str` specific parameter (e.g all, purchased,
            available, reserved ...) to use for filtering gifts; default
            is `all`.

            filter_by_date: `bool` if true, filtering by date is enabled,
            default is `false`.

            start_date: UTC datetime string, it must be less than end date.

                If only end_date is specified, the gifts will be filtered
                by dates <= end_date.

            end_date: UTC datetime string, it must be greater than start date.

        db(Session): the database session

    Response:

        Returns CustomResponse with 200 status code, message,
        and data: a List[Dict[str,Any]] containing all the gifts under
        the filter parameter.


    Exception:

        CustomException: If no gifts found or server error.
    """

    response, exception = gifts_filter(request, db)

    if exception:
        raise exception
    return response


@gift_router.post("/payment-options/bank")
async def add_bank_details(
    request: BankSchema,
    db: Session = Depends(get_db),
) -> CustomResponse:
    """Add new Bank Details.

    Args:
        request (BankSchema): Bank details
        db (Session, optional): Database session. Defaults to Depends(get_db).

    Raises:
        CustomException: If organization does not exist

    Returns:
        CustomResponse: Created bank details
    """

    try:
        bank_details = add_bank_account(request, db)
    except Exception as e:
        raise e
    return bank_details


@gift_router.post("/payment-options/wallet")
async def add_wallet_details(
    request: WalletSchema,
    db: Session = Depends(get_db),
) -> CustomResponse:
    """Add new Payment Wallet Details.

    Args:
        request (WalletSchema): Wallet details
        db (Session, optional): Database session. Defaults to Depends(get_db).

    Raises:
        CustomException: If organization does not exist

    Returns:
        CustomResponse: Created wallet details
    """

    try:
        wallet_details = add_wallet(request, db)
    except Exception as e:
        raise e
    return wallet_details
