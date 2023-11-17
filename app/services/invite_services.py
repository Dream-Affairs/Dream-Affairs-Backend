"""Invite services."""
from typing import Any, Dict
from uuid import uuid4

from sqlalchemy.orm.session import Session

from app.api.models.account_models import Account
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
        .filter(OrganizationMember.account.has(email=member.email))
        .first()
    )
    if member_exists:
        raise CustomException(
            status_code=400,
            message="Member has already been invited",
            data={"email": member.email},
        )

    # Check if member has an account
    member_account = (
        db.query(Account).filter(Account.email == member.email).first()
    )
    if not member_account:
        # Create account
        try:
            # split name to get first and last name
            name = member.name.split(" ")
            first_name = name[0]
            last_name = name[1] if len(name) > 1 else None

            member_account = Account(
                id=uuid4().hex,
                first_name=first_name,
                last_name=last_name,
                email=member.email,
                password_hash=" ",  # nosec
            )
            db.add(member_account)
            db.commit()
            db.refresh(member_account)
        except Exception as exc:
            print(exc)
            raise CustomException(
                status_code=500,
                message="Failed to create account",
                data={"email": member.email},
            ) from exc

    # Generate invite token
    invite_token = uuid4().hex

    # Invite new member
    try:
        new_member = OrganizationMember(
            id=uuid4().hex,
            account_id=member_account.id,
            organization_id=member.organization_id,
            organization_role_id=member.role_id,
            invite_token=invite_token,
        )
        db.add(new_member)
        db.commit()
        db.refresh(new_member)
    except Exception as exc:
        raise CustomException(
            status_code=500,
            message="Failed to invite new member",
            data={"organization_id": member.organization_id},
        ) from exc

    return {
        "id": new_member.id,
        "name": member.name,
        "email": member.email,
        "role": role.name,
        "organization": organization.name,
        "invite_token": new_member.invite_token,
        "is_accepted": new_member.is_accepted,
    }


def accept_invite(db: Session, invite_token: str) -> Dict[str, Any]:
    """Accept an invite.

    Args:
        db (Session): Database session
        invite_token (str): Invite token

    Raises:
        CustomException: If token is invalid

    Returns:
        dict: Member details
    """
    # Check if invite token is valid
    member = (
        db.query(OrganizationMember)
        .filter(OrganizationMember.invite_token == invite_token)
        .first()
    )
    if not member:
        raise CustomException(
            status_code=400,
            message="Invalid invite token",
            data={"invite_token": invite_token},
        )

    # Check if member has already accepted invite
    if member.is_accepted:
        raise CustomException(
            status_code=400,
            message="Invite has already been accepted",
            data={"invite_token": invite_token},
        )

    # Accept invite
    try:
        member.is_accepted = True
        db.commit()
        db.refresh(member)
    except Exception as exc:
        raise CustomException(
            status_code=500,
            message="Failed to accept invite",
            data={"invite_token": invite_token},
        ) from exc

    return {
        "id": member.id,
        "name": f"{member.account.first_name} {member.account.last_name}",
        "email": member.account.email,
        "role": member.member_role.name,
        "organization": member.organization.name,
        "invite_token": member.invite_token,
        "is_accepted": member.is_accepted,
    }