"""SSO router module."""
from fastapi import APIRouter, BackgroundTasks, Depends, Request, status
from fastapi_sso.sso.google import GoogleSSO
from sqlalchemy.orm import Session

from app.api.responses.custom_responses import CustomResponse
from app.api.schemas.account_schemas import AccountLogin, AccountSignup
from app.core.config import settings
from app.database.connection import get_db
from app.services.account_services import (
    create_account,
    get_account_by_email,
    login_service,
)
from app.services.sso_services import get_google_sso

router = APIRouter(
    tags=["Auth", "SSO"],
)


@router.get("/google/signup")
async def google_signup(google_sso: GoogleSSO = Depends(get_google_sso)):
    """Google login endpoint.

    Args:
        google_sso (GoogleSSO): The GoogleSSO object.

    Returns:
        str: The login redirect url.
    """
    user = await google_sso.get_login_url()
    return user


@router.get("/google/login")
async def google_login(google_sso: GoogleSSO = Depends(get_google_sso)):
    """Google login endpoint.

    Args:
        google_sso (GoogleSSO): The GoogleSSO object.

    Returns:
        str: The login redirect url.
    """
    user = await google_sso.get_login_url()
    return user


@router.get("/google/callback")
async def google_callback(
    request: Request,
    background_tasks: BackgroundTasks,
    google_sso: GoogleSSO = Depends(get_google_sso),
    db: Session = Depends(get_db),
):
    """Google callback endpoint.

    Args:
        request (Request): The request object.
        google_sso (GoogleSSO): The GoogleSSO object.

    Returns:
        User: The user object.
    """
    user = await google_sso.verify_and_process(request)

    if get_account_by_email(email=user.email, db=db):
        return login_service(
            db=db,
            user_credentials=AccountLogin(
                email=user.email,
                password=settings.AUTH_SECRET_KEY,
                provider="google",
            ),
        )

    data = AccountSignup(
        email=user.email,
        password=settings.AUTH_SECRET_KEY,
        confirm_password=settings.AUTH_SECRET_KEY,
        first_name=user.first_name,
        partner_name="",
        provider="google",
        location="",
    )
    _, err = create_account(data, background_tasks, db)

    if err:
        raise err

    return CustomResponse(
        status_code=status.HTTP_200_OK,
        message="User created successfully",
    )
