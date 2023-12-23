"""This module defines the router for the role endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm.session import Session

from app.api.middlewares.authorization import (
    Authorize,
    is_authenticated,
    is_org_authorized,
)
from app.api.responses.custom_responses import CustomResponse
from app.api.schemas.organization_schemas import (
    InviteMemberSchema,
    OrganizationCreate,
    OrganizationUpdate,
)
from app.database.connection import get_db
from app.services.organization_services import (
    accept_invite,
    create_organization,
    delete_organization,
    get_all_organizations,
    get_members,
    get_organization,
    invite_member,
    suspend_member,
    update_organization_details,
)

router = APIRouter(prefix="/organization", tags=["Organization"])


@router.post("")
async def create_user_organization(
    req: OrganizationCreate,
    db: Session = Depends(get_db),
    auth: Authorize = Depends(is_authenticated),
) -> CustomResponse:
    """Create an organization.

    Args:
        req (OrganizationCreate): Organization details
        db (Session, optional): Database session. Defaults to Depends(get_db).

    Raises:
        CustomException: If organization does not exist

    Returns:
        CustomResponse: Organization details
    """
    try:
        organization_details = await create_organization(
            db, auth.account.id, req
        )
    except Exception as e:
        raise e
    return CustomResponse(
        status_code=201,
        message="Organization created successfully",
        data=organization_details,
    )


@router.get("/all")
async def get_user_organizations(
    db: Session = Depends(get_db),  # pylint: disable=unused-argument
    auth: Authorize = Depends(  # pylint: disable=unused-argument
        is_authenticated
    ),
) -> CustomResponse:
    """Get an organization.

    Args:
        account_id (str): Account ID
        db (Session, optional): Database session. Defaults to Depends(get_db).

    Raises:
        CustomException: If organization does not exist

    Returns:
        CustomResponse: List of organizations
    """
    return CustomResponse(
        status_code=200,
        message="Organization retrieved successfully",
        data=get_all_organizations(account_id=auth.account.id, db=db),
    )


@router.get("")
async def get_user_organization(
    db: Session = Depends(get_db),  # pylint: disable=unused-argument
    auth: Authorize = Depends(  # pylint: disable=unused-argument
        is_org_authorized
    ),
):
    """Get an organization.

    Args:
        account_id (str): Account ID
        db (Session, optional): Database session. Defaults to Depends(get_db).

    Raises:
        CustomException: If organization does not exist

    Returns:
        CustomResponse: List of organizations
    """
    return CustomResponse(
        status_code=200,
        message="Organization retrieved successfully",
        data=get_organization(
            db,
            auth.member.organization_id,
        ),
    )


@router.put("")
async def update_user_organization(
    req: OrganizationUpdate,
    db: Session = Depends(get_db),
    auth: Authorize = Depends(is_authenticated),
) -> CustomResponse:
    """Update an organization.

    Args:
        organization_id (str): Organization ID
        req (OrganizationUpdate): Organization details
        db (Session, optional): Database session. Defaults to Depends(get_db).

    Raises:
        CustomException: If organization does not exist

    Returns:
        CustomResponse: Organization details
    """
    try:
        organization_details = update_organization_details(db, req, auth)
    except Exception as e:
        raise e
    return CustomResponse(
        status_code=200,
        message="Organization updated successfully",
        data=organization_details,
    )


@router.delete("")
async def delete_user_organization(
    email: str,
    auth: Authorize = Depends(is_authenticated),
    db: Session = Depends(get_db),
) -> CustomResponse:
    """Delete an organization.
    PLEASE NOTE THAT THIS IS FOR TESTING PURPOSES ONLY!!!
    Args:
        organization_id (str): Organization ID
        db (Session, optional): Database session. Defaults to Depends(get_db).

    Raises:
        CustomException: If organization does not exist

    Returns:
        CustomResponse: Organization details
    """
    if email != "hngxa31@gmail.com":
        return CustomResponse(
            status_code=401,
            message="You are not authorized to perform this action",
            data="",
        )
    try:
        delete_organization(db, auth.member.organization_id)
    except Exception as e:
        raise e
    return CustomResponse(
        status_code=200,
        message="Organization deleted successfully",
        data="",
    )


@router.post("/invite")
async def invite_new_member(
    invite: InviteMemberSchema,
    db: Session = Depends(get_db),
    auth: Authorize = Depends(is_authenticated),
) -> CustomResponse:
    """Invite a new member.

    Args:
        role (InviteMember): Member details
        db (Session, optional): Database session. Defaults to Depends(get_db).

    Raises:
        CustomException: If organization does not exist

    Returns:
        CustomResponse: Role details
    """
    try:
        member_details = invite_member(db, invite, auth.member.organization_id)
    except Exception as e:
        raise e
    return CustomResponse(
        status_code=200,
        message="Invite sent successfully",
        data=member_details,
    )


@router.get("/members")
async def get_organization_members(
    db: Session = Depends(get_db),
    auth: Authorize = Depends(is_authenticated),
) -> CustomResponse:
    """Get all organization members.

    Args:
        db (Session, optional): Database session. Defaults to Depends(get_db).

    Raises:
        CustomException: If organization does not exist

    Returns:
        CustomResponse: List of invites
    """
    try:
        invites = await get_members(db, auth.member.organization_id)
    except Exception as e:
        raise e
    return CustomResponse(
        status_code=200,
        message="Invites retrieved successfully",
        data=invites,
    )


# An endpoint to accept an invite
@router.get("/invite/accept/{invite_token}")
async def accept_invitation(
    invite_token: str,
    db: Session = Depends(get_db),
) -> CustomResponse:
    """Accept an invite.

    Args:
        invite_token (str): Invite token
        db (Session, optional): Database session. Defaults to Depends(get_db).

    Raises:
        CustomException: If token is invalid

    Returns:
        CustomResponse: Member details
    """
    try:
        member_details = accept_invite(db, invite_token)
    except Exception as e:
        raise e
    return CustomResponse(
        status_code=200,
        message="Invite accepted successfully",
        data=member_details,
    )


@router.patch("/{member_id}")
async def suspend_unsuspend_membership(
    member_id: str,
    auth: Authorize = Depends(is_authenticated),
    db: Session = Depends(get_db),
) -> CustomResponse:
    """Suspend and unsuspend a member.

    Args:
        member_id (str): Member ID
        db (Session, optional): Database session. Defaults to Depends(get_db).

    Raises:
        CustomException: If token is invalid

    Returns:
        CustomResponse: Member details
    """
    try:
        member_details = suspend_member(
            db, auth.member.organization_id, member_id
        )
    except Exception as e:
        raise e
    return CustomResponse(
        status_code=200,
        message="Member suspended successfully",
        data=member_details,
    )
