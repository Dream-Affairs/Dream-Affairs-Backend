"""This module defines the router for the role endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm.session import Session

from app.api.responses.custom_responses import CustomResponse
from app.api.schemas.invite_schemas import InviteMember
from app.database.connection import get_db
from app.services.invite_services import invite_new_member

router = APIRouter(tags=["Invites"])


@router.post("/invites")
async def invite_member(
    role: InviteMember, db: Session = Depends(get_db)
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
        member_details = invite_new_member(db, role)
    except Exception as e:
        raise e
    return CustomResponse(
        status_code=200,
        message="Role created successfully",
        data=member_details,
    )
