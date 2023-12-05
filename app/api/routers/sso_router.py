"""SSO router module."""
from fastapi import APIRouter, Depends, Request
from fastapi_sso.sso.google import GoogleSSO

from app.services.sso_services import get_google_sso

router = APIRouter(
    tags=["Auth", "SSO"],
)


@router.get("/google/login")
async def google_login(google_sso: GoogleSSO = Depends(get_google_sso)):
    """Google login endpoint.

    Args:
        google_sso (GoogleSSO): The GoogleSSO object.

    Returns:
        str: The login redirect url.
    """
    return await google_sso.get_login_redirect()


@router.get("/google/callback")
async def google_callback(
    request: Request, google_sso: GoogleSSO = Depends(get_google_sso)
):
    """Google callback endpoint.

    Args:
        request (Request): The request object.
        google_sso (GoogleSSO): The GoogleSSO object.

    Returns:
        User: The user object.
    """
    user = await google_sso.verify_and_process(request)
    return user
