"""This module defines the authorization middleware."""

from fastapi import Depends, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.models.account_models import Account
from app.api.models.organization_models import OrganizationMember
from app.api.responses.custom_responses import CustomException
from app.api.schemas.organization_schemas import AuthorizeOrganizationSchema
from app.database.connection import get_db
from app.services.account_services import decode_token
from app.services.roles_services import RoleService


# create an abject that returns the object
# of the current account, the organization_member and
# the role and permissions
class Authorize(BaseModel):
    """Authorized Account.

    Attributes:
        account (Account): Account object
        organization_member (OrganizationMember): Organization Member object
        role (Role): Role object
        permissions (List[str]): List of permissions
    """

    member: AuthorizeOrganizationSchema
    role: RoleService


def is_authenticated(token: str = Header(...), db: Session = Depends(get_db)):
    """Check if the user is authenticated.

    Args:
        token (str): The JWT token.
        db (Session): The database session. (Dependency)

    Returns:
        Account: The authenticated user account.

    Raises:
        HTTPException: If the token is invalid.
    """
    if token is None or not token.startswith("Bearer "):
        raise CustomException(
            status_code=401,
            message="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Remove "Bearer " from token
    token = token.split("Bearer ")[1]

    data = decode_token(token, is_authenticate=True)
    if data is None:
        raise CustomException(
            status_code=401,
            message="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    account_id = data["account_id"]
    # check if the account exists
    account = db.query(Account).filter(Account.id == account_id).first()
    if account is None:
        raise CustomException(
            status_code=401,
            message="Unkown account",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # check if the organization member exists
    organization_member = (
        db.query(OrganizationMember)
        .filter(OrganizationMember.account_id == account_id)
        .first()
    )
    if organization_member is None:
        raise CustomException(
            status_code=401,
            message="Unkown organization member",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return Authorize(
        member=AuthorizeOrganizationSchema(
            id=organization_member.id,
            name=organization_member.organization.name,
            account_id=organization_member.account_id,
            organization_id=organization_member.organization_id,
        ),
        role=RoleService().get_role(
            db, organization_member.member_role.role_id
        ),
    )
