"""This module defines the FastAPI API endpoints for user authentication."""


from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.responses.custom_responses import CustomResponse
from app.api.schemas.account_schemas import (
    AccountLogin,
    AccountSignup,
    ForgotPasswordData,
    ResetPasswordData,
)
from app.database.connection import get_db
from app.services.account_services import (
    create_account,
    forgot_password_service,
    login_service,
    reset_password_service,
    verify_account_service,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup")
def signup(
    user: AccountSignup,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> CustomResponse:
    """# Create a new user account.

    This endpoint creates a new user account and returns a success message if
    the account is created successfully.

    ## Args:

    - `user (AccountSchema)`: The user account information.
    - `db (Session)`: The database session. (Dependency)
    - `status_code (int)`: The HTTP status code to return. (Default: 201)
    - `response_model (AccountResponse)`: The response model for the created
        account.

    ## Returns:

    - `AccountResponse`: The created user account.

    ## Raises:

    - CustomException

    ## Examples:

    ```curl
    curl -X 'POST'
      'http://localhost:8000/auth/signup'
        -H 'accept: application/json'
        -H 'Content-Type: application/json'
        -d '{
        "email": "
        "password": "password",
        "confirm_password": "password",
        "first_name": "John",
        "last_name": "Doe"
        }'
    ```

    ```python
    import requests

    url = "http://localhost:8000/auth/signup"

    payload = {
        "email": "email@example.com",
        "password": "password",
        "confirm_password": "password",
        "first_name": "John",
        "last_name": "Doe"
    }

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, headers=headers, json=payload)

    print(response.text)
    ```

    Response:

    ```json

    {
        "status_code": 201,
        "message": "Account created successfully",
        "data": ""
    }
    ```

    Error Response:
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
    ```
    """

    if user.password != user.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    _, err = create_account(user, background_tasks, db)

    if err:
        raise err

    return CustomResponse(
        status_code=status.HTTP_201_CREATED,
        message="Account created successfully",
        data="",
    )


@router.post("/login")
def login(
    user_credentials: AccountLogin,
    db: Session = Depends(get_db),
) -> CustomResponse:
    """# Login to an existing user account.

    This endpoint logs a user into their account and returns a success message
    if the login is successful.

    ## Args:

    - `user_credentials (AccountLogin)`: The user account credentials.
    - `db (Session)`: The database session. (Dependency)
    - `status_code (int)`: The HTTP status code to return. (Default: 200)
    - `response_model (AccountResponse)`: The response model for the created
        account.

    ## Returns:

    - `AccountResponse`: The created user account.

    ## Raises:

    - CustomException

    ## Examples:

    ```curl
    curl -X 'POST'
        'http://localhost:8000/auth/login'
        -H 'accept: application/json'
        -H 'Content-Type: application/json'
        -d '{
        "email": "example@email.com",
        "password": "password"
        }'
    ```

    Python Example:
    ```python
    import requests

    url = "http://localhost:8000/auth/login"

    payload = {
        "email": "example@email.com",
        "password": "password"
    }
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, headers=headers, json=payload)

    print(response.text)
    ```

    Response:

        ```json
        {
            "status_code": 200,
            "message": "Login successful",
            "data": {
                "token": "<token>",
                is_2fa_enabled: false,
                is_verified: true
            }
        }
        ```

    Error Response:

    ```json
    {
        "status_code": 400,
        "detail": "Invalid email or password"
    }
    ```
    """
    res, err = login_service(db, user_credentials)

    if err:
        raise err

    return CustomResponse(
        status_code=status.HTTP_200_OK, message="Login successful", data=res
    )


@router.post("/verify-account")
def verify_account(
    token: str, db: Session = Depends(get_db)
) -> CustomResponse:
    """# Verify a user account.

    This endpoint verifies a user account and returns a success message if the
    account is verified successfully.

    ## Args:

    - `token_data (VerifyAccountTokenData)`: The data associated with the
        account verification token.
    - `db (Session)`: The database session. (Dependency)
    - `status_code (int)`: The HTTP status code to return. (Default: 200)
    - `response_model (AccountResponse)`: The response model for the created
        account.

    ## Returns:

    - `AccountResponse`: The created user account.

    ## Raises:

    - CustomException

    ## Examples:

        ```curl
        curl -X 'POST'
            'http://localhost:8000/auth/verify-account'
            -H 'accept: application/json'
            -H 'Content-Type: application/json'
            -d '{
            "token": "<token>"
            }'
        ```
    Python Example:
    ```python
    import requests

    url = "http://localhost:8000/auth/verify-account"

    payload = {
        "token": "<token>"
    }
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, headers=headers, json=payload)

    print(response.text)
    ```
    Response:
    ```json
    {
        "status_code": 200,
        "message": "Account verified successfully",
        "data": ""
    }
    ```
    Error Response:
    ```json
    {
        "status_code": 400,
        "detail": "Invalid or expired token"
    }
    ```
    """

    _, err = verify_account_service(token, db)

    if err:
        raise err

    return CustomResponse(
        status_code=status.HTTP_200_OK,
        message="Account verified successfully",
    )


@router.post("/forgot-password")
def user_forgot_password(
    user_data: ForgotPasswordData,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> CustomResponse:
    """# Send a reset password email.

    This endpoint sends a reset password email to the user and returns a
    success message if the email is sent successfully.

    ## Args:

    - `user_data (ForgotPasswordData)`: The user account email.
    - `db (Session)`: The database session. (Dependency)
    - `status_code (int)`: The HTTP status code to return. (Default: 200)
    - `response_model (AccountResponse)`: The response model for the created
        account.

    ## Returns:

    - `message`: The result of the `forgot_password_service` function.

    ## Raises:

    - CustomException

    ## Examples:

    ```curl
    curl -X 'POST'
        'http://localhost:8000/auth/forgot-password'
        -H 'accept: application/json'
        -H 'Content-Type: application/json'
        -d '{
        "email": "example@email.com"
        }'
    ```
    Python Example:
    ```python
    import requests

    url = "http://localhost:8000/auth/forgot-password"

    payload = {
        "email": "example@email.com"
    }

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, headers=headers, json=payload)

    print(response.text)
    ```

    Response:

    ```json
    {
        "status_code": 200,
        "message": "Reset password email sent successfully",
        "data": "An email has been sent to your email address with
          instructions on how to reset your password"
    }
    ```
    Error Response:
    ```json
    {
        "status_code": 400,
        "detail": "User not found"
    }
    ```
    """
    res, err = forgot_password_service(user_data, background_tasks, db)

    if err:
        raise err

    return CustomResponse(
        status_code=status.HTTP_200_OK,
        message="Reset password email sent successfully",
        data=res,
    )


@router.post("/reset-password")
def reset_password(
    token_data: ResetPasswordData,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> CustomResponse:
    """# Reset a user's password.

    This endpoint resets a user's password and returns a success message if the
    password is reset successfully.

    ## Args:

    - `token_data (ResetPasswordData)`: The data associated with the reset
        password token.
    - `db (Session)`: The database session. (Dependency)
    - `status_code (int)`: The HTTP status code to return. (Default: 200)
    - `response_model (str)`: The response model for the created account.

    ## Returns:

    - `message`: The result of the `reset_password_service` function.

    ## Raises:

    - CustomException

    ## Examples:

    ```curl
    curl -X 'POST'
        'http://localhost:8000/auth/reset-password'
        -H 'accept: application/json'
        -H 'Content-Type: application/json'
        -d '{
            token: "<token>",
            password: "password",
            confirm_password: "password"
        }'
    ```
    Http:
    ```http
    POST /auth/reset-password HTTP/1.1
    Host: localhost:8000
    Content-Type: application/json
    accept: application/json

    {
        "token": "<token>",
        "password": "password",
        "confirm_password": "password"
    }

    ```

    Response:

    ```json
    {
        "status_code": 200,
        "message": "Password reset successful"
    }
    ```
    Error Response:

    ```json
    {
        "status_code": 400,
        "detail": "Invalid or expired token"
    }
    ```
    """

    _, err = reset_password_service(token_data, db, background_tasks)

    if err:
        raise err

    return CustomResponse(
        status_code=status.HTTP_200_OK, message="Password reset successful"
    )
