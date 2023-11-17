"""Invite services."""
from typing import Any, Dict
from uuid import uuid4

from sqlalchemy.orm.session import Session

from app.api.models.organization_models import (
    Organization,
    OrganizationMember,
    OrganizationRole,
)
from app.api.responses.custom_responses import CustomException
from app.api.schemas.invite_schemas import InviteMember


def invite_new_member(db: Session, member: InviteMember) -> Dict[str, Any]:
    """Invite a new member to an organization.

    Args:
        db (Session): Database session
        member (InviteMember): Member details

    Raises:
        CustomException: If organization does not exist
        CustomException: If role does not exist

    Returns:
        dict: Member details
    """
    # Check if organization exists
    organization = (
        db.query(Organization)
        .filter(Organization.id == member.organization_id)
        .first()
    )
    if not organization:
        raise CustomException(
            status_code=404,
            message="Organization not found",
            data={"organization_id": member.organization_id},
        )

    # Check if role exists
    role = (
        db.query(OrganizationRole)
        .filter(OrganizationRole.organization_id == member.organization_id)
        .filter(OrganizationRole.id == member.role_id)
        .first()
    )
    if not role:
        raise CustomException(
            status_code=400,
            message="Role does not exist",
            data={"role_id": member.role_id},
        )

    # Check if email has already been invited
    member_exists = (
        db.query(OrganizationMember)
        .filter(OrganizationMember.organization_id == member.organization_id)
        .filter(OrganizationMember.email == member.email)
        .first()
    )
    if member_exists:
        raise CustomException(
            status_code=400,
            message="Member has already been invited",
            data={"email": member.email},
        )

    # Generate invite token
    invite_token = uuid4().hex

    # Invite new member
    try:
        new_member = OrganizationMember(
            id=uuid4().hex,
            name=member.name,
            email=member.email,
            organization_id=member.organization_id,
            organization_role_id=member.role_id,
            invite_token=invite_token,
        )
    except Exception as exc:
        raise CustomException(
            status_code=500,
            message="Failed to invite new member",
            data={"organization_id": member.organization_id},
        ) from exc

    return {
        "id": new_member.id,
        "name": new_member.name,
        "email": new_member.email,
        "role": role.name,
        "organization": organization.name,
        "invite_token": new_member.invite_token,
    }
