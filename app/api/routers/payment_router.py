"""This module defines the FastAPI API endpoints for payment."""


from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.responses.custom_responses import CustomResponse
from app.api.schemas.payment_schemas import (
    BankSchema,
    FilterAcountsEnum,
    LinkSchema,
    PaymentType,
    WalletSchema,
)
from app.database.connection import get_db
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

payment_router = APIRouter(prefix="/payment", tags=["Payment"])


@payment_router.post("/payment-options/bank")
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


@payment_router.post("/payment-options/wallet")
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


@payment_router.post("/payment-options/link")
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


@payment_router.get("/payment-options/{organization_id}/{payment_account_id}")
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


@payment_router.get("/payment-options/{organization_id}")
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


@payment_router.patch("/payment-options/bank/{bank_account_id}")
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


@payment_router.patch("/payment-options/wallet/{wallet_account_id}")
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


@payment_router.patch("/payment-options/link/{link_account_id}")
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
