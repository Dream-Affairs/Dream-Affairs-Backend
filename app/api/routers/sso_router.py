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
    prefix="/sso",
    tags=["SSO"],
)


@router.get("/google/signup")
async def google_signup(
    google_sso: GoogleSSO = Depends(get_google_sso),
) -> CustomResponse:
    """# Google signup endpoint.

    This endpoint returns the Google signup uri for the user.

    ## Args:

    - `google_sso (GoogleSSO)`: The GoogleSSO object.

    ## Returns:

    - str: The signup redirect url.

    ## Raises:

    - HTTPException: If an error occurs.

    ## Example:

    ```http
    GET /sso/google/signup HTTP/1.1
    Host: localhost:8000
    Content-Type: application/json
    accept: application/json
    ```
    Response:
    ```json
    {
        "status_code": 200,
        "message": "User Oauth Uri",
        "data": "https://accounts.google.com/o/oauth2/auth?response_type=code&
        client_id=1234567890&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2F
        sso%2Fgoogle%2Fcallback&scope=email&state=1234567890&
        access_type=offline"
    }
    ```
    """
    user = await google_sso.get_login_url()
    return user


@router.get("/google/login")
async def google_login(
    google_sso: GoogleSSO = Depends(get_google_sso),
) -> CustomResponse:
    """# Google signin endpoint.

    This endpoint returns the Google signin uri for the user.

    ## Args:

    - `google_sso (GoogleSSO)`: The GoogleSSO object.

    ## Returns:

    - `str`: The signin redirect url.

    ## Raises:

    - HTTPException: If an error occurs.

    ## Example:

    HTTP request:

    ```http
    GET /sso/google/signip HTTP/1.1
    Host: localhost:8000
    Content-Type: application/json
    accept: application/json
    ```
    Response:

    ```json
    {
        "status_code": 200,
        "message": "User Oauth Uri",
        "data": "https://accounts.google.com/o/oauth2/auth?response_type=code&
        client_id=1234567890&redirect_uri=http%3A%2F%2Flocalhost%3A8000%
        2Fsso%2Fgoogle%2Fcallback&scope=email&state=1234567890&
        access_type=offline"
    }
    ```
    """
    user = await google_sso.get_login_url()
    return CustomResponse(
        status_code=status.HTTP_200_OK,
        message="User login",
        data=user,
    )


@router.get("/google/callback")
async def google_callback(
    request: Request,
    background_tasks: BackgroundTasks,
    google_sso: GoogleSSO = Depends(get_google_sso),
    db: Session = Depends(get_db),
) -> CustomResponse:
    """# Google callback endpoint.

    This endpoint processes the Google callback and creates
      a user account if it does not exist.

    ## Args:

    - `request (Request)`: The request object.
    - `background_tasks (BackgroundTasks)`: The background
        tasks object.
    - `google_sso (GoogleSSO)`: The GoogleSSO object.
    - `db (Session)`: The database session.

    ## Returns:

    - `CustomResponse`: The response object.

    ## Raises:

    - HTTPException: If an error occurs.

    ## Example:

    HTTP request:

    ```http
    GET /sso/google/callback?code=4%2F0AX4XfWgq ...  HTTP/1.1
    Host: localhost:8000
    Content-Type: application/json
    accept: application/json
    ```
    Response:

    ```json
    {
        "status_code": 200,
        "message": "User created successfully"
    }
    ```
    or

    ```json
    {
        "status_code": 200,
        "message": "User Oauth Uri",
        "data": {
                "token": "<token>",
                is_2fa_enabled: false,
                is_verified: true
            }
    }

    Error response:

    ```json
    {
        "status_code": 400,
        "detail": "Invalid email or password"
    }

       ```json
    {
        "status_code": 400,
        "detail": "Passwords do not match"
    }
    ```
    ```json
    {
        "status_code": 400,
        "detail": "user already exists"
    }
    ```
    ```json
    {
        "status_code": 500,
        "detail": "failed to create user account"
    }
    """
    user = await google_sso.verify_and_process(request)

    if get_account_by_email(email=user.email, db=db):
        res, err = login_service(
            db=db,
            user_credentials=AccountLogin(
                email=user.email,
                password=settings.AUTH_SECRET_KEY,
                provider="google",
            ),
        )
        if err:
            raise err
        return CustomResponse(
            status_code=status.HTTP_200_OK,
            message="User Oauth Uri",
            data=res,
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
