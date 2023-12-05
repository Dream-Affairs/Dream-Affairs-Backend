"""This module contains the SSO services."""
from fastapi_sso.sso.google import GoogleSSO

from app.core.config import settings


def get_google_sso() -> GoogleSSO:
    """
    Get GoogleSSO:
        This function returns the GoogleSSO object.
        It is used to get the login redirect and verify the
        user.
    """
    return GoogleSSO(
        settings.GOOGLE_CLIENT_ID,
        settings.GOOGLE_CLIENT_SECRET,
        redirect_uri=settings.GOOGLE_REDIRECT_URI,
    )
