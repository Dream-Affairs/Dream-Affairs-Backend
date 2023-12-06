"""This module defines the router for the role endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm.session import Session

from app.api.middlewares.authorization import Authorize, is_authenticated
from app.api.responses.custom_responses import CustomResponse
from app.api.schemas.organization_schemas import (
    InviteMember,
    OrganizationUpdate,
)
from app.database.connection import get_db
from app.services.organization_services import (
    accept_invite,
    accepted_invites,
    delete_organization,
    invite_new_member,
    suspend_member,
    suspended_invites,
    update_organization_details,
)

router = APIRouter(prefix="/organization", tags=["Organization"])


@router.put("/")
async def update_organization(
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
async def delete_organizations(
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


@router.post("/invites")
async def invite_member(
    invite: InviteMember,
    db: Session = Depends(get_db),
    auth: Authorize = Depends(is_authenticated),
) -> CustomResponse:
    """Create a new role.

    Args:
        role (InviteMember): Member details
        db (Session, optional): Database session. Defaults to Depends(get_db).

    Raises:
        CustomException: If organization does not exist

    Returns:
        CustomResponse: Role details
    """
    try:
        member_details = invite_new_member(
            db, invite, auth.member.organization_id
        )
    except Exception as e:
        raise e
    return CustomResponse(
        status_code=200,
        message="Invite sent successfully",
        data=member_details,
    )


# An endpoint to accept an invite
@router.get("/invites/accept/{invite_token}")
async def accept_invitation(
    invite_token: str,
    db: Session = Depends(get_db),
    auth: Authorize = Depends(  # pylint: disable=unused-argument
        is_authenticated
    ),
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


# An endpoint to get all accepted invites
@router.get("/invites/accepted")
async def get_all_accepted_invites(
    auth: Authorize = Depends(is_authenticated), db: Session = Depends(get_db)
) -> CustomResponse:
    """Get all accepted invites.

    Args:
        organization_id (str): Organization ID
        db (Session, optional): Database session. Defaults to Depends(get_db).

    Raises:
        CustomException: If organization does not exist

    Returns:
        CustomResponse: List of member details
    """
    try:
        accepted_members_details = accepted_invites(
            db, auth.member.organization_id
        )
    except Exception as e:
        raise e
    return CustomResponse(
        status_code=200,
        message="Accepted invites fetched successfully",
        data=accepted_members_details,
    )


@router.get("/invites/suspended")
async def get_all_suspended_invites(
    auth: Authorize = Depends(is_authenticated), db: Session = Depends(get_db)
) -> CustomResponse:
    """Get all suspended invites.

    Args:
        organization_id (str): Organization ID
        db (Session, optional): Database session. Defaults to Depends(get_db).

    Raises:
        CustomException: If organization does not exist

    Returns:
        CustomResponse: List of member details
    """
    try:
        suspended_members_details = suspended_invites(
            db, auth.member.organization_id
        )
    except Exception as e:
        raise e
    return CustomResponse(
        status_code=200,
        message="Suspended invites fetched successfully",
        data=suspended_members_details,
    )


@router.put("/invites/suspend/{member_id}")
async def suspend_membership(
    member_id: str,
    auth: Authorize = Depends(is_authenticated),
    db: Session = Depends(get_db),
) -> CustomResponse:
    """Suspend a member.

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
