"""This module defines the FastAPI API endpoints for registry/gift."""


from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.responses.custom_responses import CustomResponse
from app.api.schemas.gift_schemas import (
    AddCashGift,
    AddProductGift,
    BankSchema,
    EditProductGift,
    FilterAcountsEnum,
    FilterGiftSchema,
    LinkSchema,
    PaymentType,
    WalletSchema,
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
from app.services.payment_services import (
    add_bank_account,
    add_payment_link,
    add_wallet,
    get_account,
    get_accounts,
    update_bank,
    update_link,
    update_wallet,
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


@gift_router.post("/payment-options/link")
async def add_payment_link_details(
    request: LinkSchema,
    db: Session = Depends(get_db),
) -> CustomResponse:
    """Add new Payment Link Details. (e.g PayPal,Payoneer,...)

    Args:
        request (LinkSchema): Wallet details
        db (Session, optional): Database session. Defaults to Depends(get_db).

    Raises:
        CustomException: If organization does not exist

    Returns:
        CustomResponse: Created payment link details
    """

    try:
        link_details = add_payment_link(request, db)
    except Exception as e:
        raise e
    return link_details


@gift_router.get("/payment-options/{organization_id}/{payment_account_id}")
async def get_payment_account(
    organization_id: str,
    payment_account_id: str,
    payment_type: PaymentType,
    db: Session = Depends(get_db),
) -> CustomResponse:
    """Get a single payment account details.
    Args:
        organization_id, payment_account_id, payment_type(bank,wallet,link).
        db (Session, optional): Database session. Defaults to Depends(get_db).

    Raises:
        CustomException: If organization or payment account does not exist

    Returns:
        CustomResponse: Retrieved payment details
    """
    try:
        payment_account = get_account(
            organization_id,
            payment_account_id,
            payment_type,
            db,
        )
    except Exception as e:
        raise e

    return payment_account


@gift_router.get("/payment-options/{organization_id}")
async def get_payment_accounts(
    organization_id: str,
    filter_by: FilterAcountsEnum,
    db: Session = Depends(get_db),
) -> CustomResponse:
    """Get  payment accounts details.

    Args:
        organization_id, filter_by(all,default).

        db (Session, optional): Database session. Defaults to Depends(get_db).

    Raises:

        CustomException: If organization  does not exist

    Returns:

        CustomResponse: Retrieved payment details
    """
    try:
        payment_accounts = get_accounts(
            organization_id,
            filter_by,
            db,
        )
    except Exception as e:
        raise e

    return payment_accounts


@gift_router.patch("/payment-options/bank/{bank_account_id}")
async def update_bank_details(
    bank_account_id: str,
    request: BankSchema,
    db: Session = Depends(get_db),
) -> CustomResponse:
    """Update bank account details.

    Args:
        bank_account_id, request(BankSchema).
        db (Session, optional): Database session. Defaults to Depends(get_db).
    Raises:
        CustomException: If something goes wrong
    Returns:
        CustomResponse: Updated payment details
    """
    try:
        updated_bank_details = update_bank(
            bank_account_id,
            request,
            db,
        )
    except Exception as e:
        raise e

    return updated_bank_details


@gift_router.patch("/payment-options/wallet/{wallet_account_id}")
async def update_wallet_details(
    wallet_account_id: str,
    request: WalletSchema,
    db: Session = Depends(get_db),
) -> CustomResponse:
    """Update wallet account details.

    Args:
        wallet_account_id, request(WalletSchema).
        db (Session, optional): Database session. Defaults to Depends(get_db).
    Raises:
        CustomException: If something goes wrong
    Returns:
        CustomResponse: Updated payment details
    """
    try:
        updated_wallet_details = update_wallet(
            wallet_account_id,
            request,
            db,
        )
    except Exception as e:
        raise e

    return updated_wallet_details


@gift_router.patch("/payment-options/link/{link_account_id}")
async def update_link_details(
    link_account_id: str,
    request: LinkSchema,
    db: Session = Depends(get_db),
) -> CustomResponse:
    """Update link account details.

    Args:
        link_account_id, request(LinkSchema).
        db (Session, optional): Database session. Defaults to Depends(get_db).
    Raises:
        CustomException: If something goes wrong
    Returns:
        CustomResponse: Updated payment details
    """
    try:
        updated_link_details = update_link(
            link_account_id,
            request,
            db,
        )
    except Exception as e:
        raise e

    return updated_link_details


@gift_router.post("/{organization_id}/cash-gifts")
async def add_cash_funds_gift(
    organization_id: str,
    request: AddCashGift,
    db: Session = Depends(get_db),
) -> CustomResponse:
    """Add a cash funds gift to organization registry.

    Args:
        organization_id, request(AddCashGift).
        db (Session, optional): Database session. Defaults to Depends(get_db).
    Raises:
        CustomException: If something goes wrong
    Returns:
        CustomResponse: Added gift details
    """
    try:
        added_gift_details = add_cash_gift(
            organization_id,
            request,
            db,
        )
    except Exception as e:
        raise e

    return added_gift_details
