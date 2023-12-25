"""This module defines the authorization middleware."""

from fastapi import Depends, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.middlewares.jwt_bearer import (
    HTTPAuthorizationCredentials,
    bearer_scheme,
)
from app.api.models.account_models import Account
from app.api.models.organization_models import OrganizationMember
from app.api.responses.custom_responses import CustomException
from app.api.schemas.account_schemas import AccountAuthorized
from app.api.schemas.organization_schemas import AuthorizeOrganizationSchema
from app.database.connection import get_db
from app.services.account_services import decode_data, decode_token
from app.services.roles_services import RoleService


class Authorize(BaseModel):
    """Authorized Account.

    Attributes:
        account (Account): Account object
        organization_member (OrganizationMember): Organization Member object
        role (Role): Role object
        permissions (List[str]): List of permissions
    """

    account: AccountAuthorized | None = None
    member: AuthorizeOrganizationSchema | None = None
    role: RoleService | None = None


def is_authenticated(
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Authorize:
    """Check if the user is authenticated.

    Args:
        token (str): The JWT token.
        db (Session): The database session. (Dependency)

    Returns:
        Account: The authenticated user account.

    Raises:
        HTTPException: If the token is invalid.
    """
    authorize = Authorize()
    if token.credentials is None:
        raise CustomException(
            status_code=401,
            message="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Remove "Bearer " from token

    data = decode_token(token, is_authenticate=True)

    account_id = data["account_id"]
    # check if the account exists
    account = db.query(Account).filter(Account.id == account_id).first()
    if account is None:
        raise CustomException(
            status_code=401,
            message="Unkown user",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # check if the organization member exists
    authorize.account = AccountAuthorized(
        id=account.id,
        first_name=account.first_name,
        last_name=account.last_name or "",
        email=account.email,
        is_verified=account.is_verified,
    )
    return authorize


def is_org_authorized(
    req: Request,
    db: Session = Depends(get_db),
    auth: Authorize = Depends(is_authenticated),
) -> Authorize:
    """Get the current organization member.

    Args:
        authorization (str): Authorization header
        db (Session): Database session. (Dependency)
        auth (Authorize): Authorized user. (Dependency)

    Returns:
        Authorize: Authorized user
    """
    try:
        emxsidqw = req.cookies["emxsidqw"]
        if emxsidqw is None:
            raise CustomException(
                status_code=401,
                message="Unauthorized",
            )
    except KeyError as e:
        raise CustomException(
            status_code=401,
            message="Please select an event",
        ) from e

    emxsidqw = decode_data(emxsidqw)
    member_instance = (
        db.query(OrganizationMember)
        .filter(
            OrganizationMember.account_id == auth.account.id,
            OrganizationMember.organization_id == emxsidqw,
        )
        .first()
    )
    if member_instance is None:
        raise CustomException(
            status_code=401,
            message="Unauthorized",
        )
    auth.member = AuthorizeOrganizationSchema(
        id=member_instance.id,
        name=member_instance.organization.name,
        account_id=member_instance.account_id,
        organization_id=member_instance.organization_id,
        role_id=member_instance.organization_role_id,
    )
    return auth
