"""This module defines the router for the role endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm.session import Session

from app.api.responses.custom_responses import CustomResponse
from app.api.schemas.invite_schemas import InviteMember
from app.database.connection import get_db
from app.services.invite_services import (
    accept_invite,
    accepted_invites,
    suspended_invites,
    invite_new_member,
)

router = APIRouter(tags=["Invites"])


@router.post("/invites")
async def invite_member(
    invite: InviteMember, db: Session = Depends(get_db)
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
        member_details = invite_new_member(db, invite)
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
    invite_token: str, db: Session = Depends(get_db)
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
@router.get("/invites/accepted/{organization_id}")
async def get_all_accepted_invites(
    organization_id: str, db: Session = Depends(get_db)
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
        accepted_members_details = accepted_invites(db, organization_id)
    except Exception as e:
        raise e
    return CustomResponse(
        status_code=200,
        message="Accepted invites fetched successfully",
        data=accepted_members_details,
    )
