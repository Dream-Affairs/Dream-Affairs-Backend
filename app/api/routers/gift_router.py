"""This module defines the FastAPI API endpoints for registry/gift."""


from typing import Any, Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.middlewares.authorization import Authorize, is_org_authorized
from app.api.responses.custom_responses import CustomException, CustomResponse
from app.api.schemas.gift_schemas import (
    AddCashGift,
    AddProductGift,
    BankSchema,
    EditProductGift,
    FilterAcountsEnum,
    FilterGiftSchema,
    GiftType,
    LinkSchema,
    PaymentType,
    WalletSchema,
)
from app.database.connection import get_db
from app.services.gift_payment_services import (
    add_bank_account,
    add_payment_link,
    add_wallet,
    get_account,
    get_accounts,
    update_bank,
    update_link,
    update_wallet,
)
from app.services.gift_services import (
    add_cash_gift,
    add_product_gift_,
    delete_a_gift,
    edit_product_gift_,
    fetch_gift,
    gifts_filter,
)

router = APIRouter(prefix="/gift", tags=["Registry"])


@router.post("/{gift_type}")
async def add_gift(
    gift_type: GiftType,
    db: Session = Depends(get_db),
    auth: Authorize = Depends(is_org_authorized),
    product_request: Optional[AddProductGift] = None,
    cash_request: Optional[AddCashGift] = None,
) -> Any:
    """Add a New  gift to Registry.

    Request:
        Method: POST;
        gift_type: must be either physical or cash
        gift_item(product or cash gift schema): Request Body containing the
        details of the gift to be added.
    Response: Returns CustomResponse with 201 status code and
        `data` which is a dictionary containing gift details.
    Exception:
        CustomException: If the user is not authenticated or
            a field is missing or internal server error.
    """
    # if gift type is physical
    if gift_type.value == "physical" and product_request:
        response, exception = add_product_gift_(
            product_request, auth.member.organization_id, db
        )
        if exception:
            raise exception

        return response
    # if gift type is cash
    if gift_type.value == "cash" and cash_request:
        try:
            added_gift_details = add_cash_gift(
                auth.member.organization_id,
                cash_request,
                db,
            )
        except Exception as e:
            raise e

        return added_gift_details

    raise CustomException(
        status_code=status.HTTP_400_BAD_REQUEST, message="Bad Request"
    )


@router.patch("/{gift_type}/{gift_id}")
async def update_gift(
    gift_type: GiftType,
    gift_id: str,
    product_request: EditProductGift,
    db: Session = Depends(get_db),
    auth: Authorize = Depends(  # pylint: disable=unused-argument
        is_org_authorized
    ),
) -> Any:
    """Update a gift in Registry.

    Request:
        Method: PATCH;
        gift_type: must be either physical or cash
        gift_id: the ID of the gift to be updated;
        gift_item(schema): Request Body containing the details of the
            gift to be updated.;
    Response: Returns CustomResponse with 201 status code and
        `data` which is a dictionary containing gift details.;
    Exception:
        CustomException: If something goes wrong.
    """
    if gift_type.value == "physical":
        response, exception = edit_product_gift_(product_request, gift_id, db)
        if exception:
            raise exception

        return response


@router.get("/{gift_id}")
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
    auth: Authorize = Depends(is_org_authorized),
) -> Any:
    """Get gifts from the Registry.

    Request:
        Method: POST;
        request (Schema):
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

    response, exception = gifts_filter(
        auth.member.organization_id,
        request,
        db,
    )

    if exception:
        raise exception
    return response


@router.post("/gift/payment/option/{payment_type}")
async def add_gift_payment_details(
    payment_type: PaymentType,
    db: Session = Depends(get_db),
    auth: Authorize = Depends(is_org_authorized),
    bank_request: Optional[BankSchema] = None,
    wallet_request: Optional[WalletSchema] = None,
    link_request: Optional[LinkSchema] = None,
) -> CustomResponse:
    """Add new Payment Details.

    Args:
        payment_type: must be either bank,wallet or link.;
        request (BankSchema or WalletSchema or LinkSchema): details of the
        particular payment option.;
    Raises:
        CustomException: If something goes wrong.;
    Returns:
        CustomResponse: Created payment details
    """
    # if bank option
    if payment_type.value == "bank" and bank_request:
        try:
            bank_details = add_bank_account(
                auth.member.organization_id,
                bank_request,
                db,
            )
        except Exception as e:
            raise e
        return bank_details

    # if wallet option
    if payment_type.value == "wallet" and wallet_request:
        try:
            wallet_details = add_wallet(
                auth.member.organization_id, wallet_request, db
            )
        except Exception as e:
            raise e
        return wallet_details
    # if link option
    if payment_type.value == "link" and link_request:
        try:
            link_details = add_payment_link(
                auth.member.organization_id,
                link_request,
                db,
            )
        except Exception as e:
            raise e
        return link_details

    raise CustomException(
        status_code=status.HTTP_400_BAD_REQUEST, message="Bad Request"
    )


@router.get("/payment/option/{payment_account_id}")
async def get_payment_account(
    payment_account_id: str,
    payment_type: PaymentType,
    db: Session = Depends(get_db),
    auth: Authorize = Depends(is_org_authorized),
) -> CustomResponse:
    """Get a single payment account details.

    Args:
        payment_account_id, payment_type(bank,wallet,link).;
    Raises:
        CustomException: If organization or payment account does not exist;
    Returns:
        CustomResponse: Retrieved payment details
    """
    try:
        payment_account = get_account(
            auth.member.organization_id,
            payment_account_id,
            payment_type,
            db,
        )
    except Exception as e:
        raise e

    return payment_account


@router.get("/payment/options")
async def get_payment_accounts(
    filter_by: FilterAcountsEnum,
    db: Session = Depends(get_db),
    auth: Authorize = Depends(is_org_authorized),
) -> CustomResponse:
    """Get  payment accounts details.

    Args:
        organization_id, filter_by(all,default).;
    Raises:
        CustomException: If something goes wrong;
    Returns:
        CustomResponse: Retrieved payment details
    """
    try:
        payment_accounts = get_accounts(
            auth.member.organization_id,
            filter_by,
            db,
        )
    except Exception as e:
        raise e

    return payment_accounts


@router.post("/gift/payment/option/{payment_type}/{payment_account_id}")
async def update_gift_payment_details(
    payment_type: PaymentType,
    payment_account_id: str,
    db: Session = Depends(get_db),
    auth: Authorize = Depends(is_org_authorized),
    bank_request: Optional[BankSchema] = None,
    wallet_request: Optional[WalletSchema] = None,
    link_request: Optional[LinkSchema] = None,
) -> CustomResponse:
    """Update gift payment details.

    Args:
        payment_type: must be either bank,wallet or link;
        payment_account_id:the id for the particular payment option,
        request(WalletSchema);
    Raises:
        CustomException: If something goes wrong;
    Returns:
        CustomResponse: Updated payment details
    """
    if payment_type.value == "bank" and bank_request:
        try:
            updated_bank_details = update_bank(
                auth.member.organization_id,
                payment_account_id,
                bank_request,
                db,
            )
        except Exception as e:
            raise e

        return updated_bank_details
    if payment_type.value == "wallet" and wallet_request:
        try:
            updated_wallet_details = update_wallet(
                auth.member.organization_id,
                payment_account_id,
                wallet_request,
                db,
            )
        except Exception as e:
            raise e

        return updated_wallet_details
    if payment_type.value == "link" and link_request:
        try:
            updated_link_details = update_link(
                auth.member.organization_id,
                payment_account_id,
                link_request,
                db,
            )
        except Exception as e:
            raise e

        return updated_link_details

    raise CustomException(
        status_code=status.HTTP_400_BAD_REQUEST, message="Bad Request"
    )
