"""This module has the code for custom jwt bearer class."""
from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.api.responses.custom_responses import CustomException


class CustomHTTPBearer(HTTPBearer):
    """Custom HTTP Bearer class to handle the authentication.

    Args:
        HTTPBearer (class): FastAPI HTTPBearer class

    Raises:
        HTTPException: If the token is invalid.
    """

    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super().__call__(
            request
        )
        if not credentials:
            raise CustomException(
                status_code=401,
                message="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return credentials


bearer_scheme = CustomHTTPBearer()
