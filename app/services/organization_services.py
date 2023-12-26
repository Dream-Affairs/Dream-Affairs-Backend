"""This module contains services for the organization model."""
from datetime import datetime
from typing import Any, Dict, List
from uuid import uuid4

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import asc

from app.api.models.account_models import Account
from app.api.models.organization_models import (
    InviteMember,
    Organization,
    OrganizationDetail,
    OrganizationMember,
    OrganizationRole,
)
from app.api.responses.custom_responses import CustomException
from app.api.schemas.organization_schemas import (
    InviteMemberSchema,
    OrganizationCreate,
    OrganizationUpdate,
)
from app.core.config import settings
from app.services.account_services import hash_password
from app.services.roles_services import RoleService


async def create_organization(
    db: Session, account_id: str, organization: OrganizationCreate
) -> Dict[str, Any]:
    """Create an organization.

    Args:
        db (Session): Database session
        account_id (str): Account ID
        organization (OrganizationCreate): Organization details

    Raises:
        CustomException: If organization already exists

    Returns:
        dict: Organization details
    """
    organization_name = organization.name.title()

    if (
        db.query(Organization)
        .filter(
            Organization.name == organization_name,
            Organization.owner == account_id,
        )
        .first()
    ):
        raise CustomException(
            status_code=400,
            message="Organization already exists",
            data={"name": organization_name},
        )
    org_id = uuid4().hex
    org = Organization(
        id=org_id,
        name=organization_name,
        owner=account_id,
        org_type=organization.event_type.title(),
        detail=OrganizationDetail(
            organization_id=org_id,
            website=organization.event_details.website,
            event_date=organization.event_details.event_date,
            event_start_time=organization.event_details.event_start_time,
            event_end_time=organization.event_details.event_end_time,
        ),
    )
    db.add(org)
    role_admin = RoleService().get_default_role(db=db, name="Admin")
    role_event_planner = RoleService().get_default_role(
        db=db, name="Event Planner"
    )
    role_guest = RoleService().get_default_role(db=db, name="Guest Manager")
    org_role = RoleService().add_role_to_organization(
        db, org.id, role_id=role_admin.id
    )
    RoleService().add_role_to_organization(
        db, org.id, role_id=role_event_planner.id
    )
    RoleService().add_role_to_organization(db, org.id, role_id=role_guest.id)

    RoleService().assign_role(
        organization_id=org.id,
        db=db,
        organization_role_id=org_role.id,
        account_id=account_id,
    )

    org_member_instance = OrganizationMember(
        id=uuid4().hex,
        account_id=account_id,
        organization_role_id=org_role.id,
        organization_id=org.id,
    )
    db.add(org_member_instance)
    db.commit()
    db.refresh(org)
    return {
        "organization_id": org.id,
        "name": org.name,
        "description": org.description if not None else "",
        "event_details": {
            "website": org.detail.website,
            "event_date": str(org.detail.event_date),
            "event_start_time": str(org.detail.event_start_time),
            "event_end_time": str(org.detail.event_end_time),
        },
    }


def get_all_organizations(
    account_id: str, db: Session
) -> List[Dict[str, Any]]:
    """Get all organizations that an account belongs to.

    Args:
        account_id (str): Account ID
        db (Session): Database session

    Returns:
        List[Dict[str, Any]]: List of organizations
    """
    query = (
        db.query(OrganizationMember)
        .filter(OrganizationMember.account_id == account_id)
        .order_by(asc(OrganizationMember.created_at))
        .all()
    )

    organizations = []
    for organization in query:
        event_date = organization.organization.detail.event_date
        event_start_time = organization.organization.detail.event_start_time
        event_end_time = organization.organization.detail.event_end_time
        organizations.append(
            {
                "id": organization.organization.id,
                "name": organization.organization.name,
                "description": organization.organization.description,
                "logo": organization.organization.logo,
                "event_details": {
                    "website": organization.organization.detail.website,
                    "event_date": str(event_date),
                    "event_start_time": str(event_start_time),
                    "event_end_time": str(event_end_time),
                },
            }
        )

    return organizations


def get_organization(db: Session, organization_id: str) -> Dict[str, Any]:
    """Get an organization.

    Args:
        db (Session): Database session
        organization_id (str): Organization ID

    Raises:
        CustomException: If organization does not exist

    Returns:
        dict: Organization details
    """
    organization = (
        db.query(Organization)
        .filter(Organization.id == organization_id)
        .first()
    )
    if not organization:
        raise CustomException(
            status_code=404,
            message="Organization not found",
            data={"organization_id": organization_id},
        )

    return {
        "id": organization.id,
        "name": organization.name,
        "description": organization.description,
        "logo": organization.logo,
        "event_details": {
            "website": organization.detail.website,
            "event_date": str(organization.detail.event_date),
            "event_start_time": str(organization.detail.event_start_time),
            "event_end_time": str(organization.detail.event_end_time),
        },
    }


async def get_members(
    db: Session,
    organization_id: str,
) -> List[Dict[str, Any]]:
    """Get all organizatoion members and invites.

    Args:
        db (Session, optional): Database session. Defaults to Depends(get_db).
        organization_id (str): Organization ID

    Raises:
        CustomException: If organization does not exist

    Returns:
        List[Dict[str, Any]]: List of invites
    """
    organization = check_organization_exists(
        db, organization_id=organization_id
    )
    if not organization:
        raise CustomException(
            status_code=404,
            message="Organization not found",
            data={"organization_id": organization_id},
        )

    query = db.query(InviteMember, OrganizationMember).filter(
        InviteMember.organization_id == organization_id
    )
    query = query.join(
        OrganizationMember,
        OrganizationMember.account_id == InviteMember.account_id,
    )
    query = query.filter(
        OrganizationMember.account_id == InviteMember.account_id
    )
    query.all()

    members = []
    unverified_members = []
    suspended_members = []

    for member in query:
        member_dict = {
            "id": member[1].id,
            "name": f"{member[1].account.first_name} \
{member[1].account.last_name or ''}",
            "email": member[1].account.email,
            "role": member[1].member_role.role.name,
            "is_accepted": member[0].is_accepted,
            "is_suspended": member[1].is_suspended,
        }

        if member[0].is_accepted and not member[1].is_suspended:
            members.append(member_dict)
        elif not member[0].is_accepted and not member[1].is_suspended:
            unverified_members.append(member_dict)
        if member[1].is_suspended:
            suspended_members.append(member_dict)

    data = {
        "members": members,
        "unverified_members": unverified_members,
        "suspended_members": suspended_members,
    }
    return data


def update_organization_details(
    db: Session, organization_id: str, data: OrganizationUpdate
) -> Dict[str, Any]:
    """Update an organization.

    Args:
        db (Session): Database session
        organization_id (str): Organization ID
        data (OrganizationUpdate): Organization details

    Raises:
        CustomException: If organization does not exist

    Returns:
        dict: Organization details
    """
    organization: Organization = check_organization_exists(
        db, organization_id=organization_id
    )
    if not organization:
        raise CustomException(
            status_code=404,
            message="Organization not found",
            data={"organization_id": organization_id},
        )

    if data.name:
        organization.name = data.name
    if data.description:
        organization.description = data.description
    if data.logo:
        organization.logo = data.logo
    if data.event_details.website:
        organization.detail.website = data.event_details.website
    if data.event_details.event_date:
        organization.detail.event_date = data.event_details.event_date
    if data.event_details.event_start_time:
        organization.detail.event_start_time = (
            data.event_details.event_start_time
        )
    if data.event_details.event_end_time:
        organization.detail.event_end_time = data.event_details.event_end_time

    organization.updated_at = datetime.utcnow()
    organization.detail.updated_at = datetime.utcnow()
    try:
        db.commit()

    except Exception as exc:
        raise CustomException(
            status_code=500,
            message="Failed to update organization details",
            data={"organization_id": organization.id},
        ) from exc

    return {
        "name": organization.name,
        "description": organization.description,
        "logo": organization.logo,
        "event_details": {
            "website": organization.detail.website,
            "event_date": str(organization.detail.event_date),
            "event_start_time": str(organization.detail.event_start_time),
            "event_end_time": str(organization.detail.event_end_time),
        },
    }


def invite_member(
    db: Session, member: InviteMemberSchema, organization_id: str
) -> Dict[str, Any]:
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
    organization = check_organization_exists(
        db, organization_id=organization_id
    )
    if not organization:
        raise CustomException(
            status_code=404,
            message="Organization not found",
            data={"organization_id": organization_id},
        )

    # Check if role exists
    role = (
        db.query(OrganizationRole)
        .filter(OrganizationRole.organization_id == organization_id)
        .filter(OrganizationRole.role_id == member.role_id)
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
        .filter(OrganizationMember.organization_id == organization_id)
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
        # try:
        # split name to get first and last name
        name = member.name.split(" ")
        first_name = name[0]
        last_name = name[1] if len(name) > 1 else None

        try:
            acc_id = uuid4().hex
            account = Account(
                id=acc_id,
                email=member.email,
                first_name=first_name,
                last_name=last_name,
                password_hash=hash_password(settings.AUTH_SECRET_KEY),
            )
            db.add(account)

            member_account = OrganizationMember(
                id=uuid4().hex,
                account_id=acc_id,
                organization_role_id=role.id,
                organization_id=organization_id,
            )
            db.add(member_account)

            invite = InviteMember(
                id=uuid4().hex,
                account_id=acc_id,
                organization_id=organization_id,
                invite_token=uuid4().hex,
            )
            db.add(invite)

            db.commit()
        except SQLAlchemyError as exc:
            db.rollback()
            raise CustomException(
                status_code=500,
                message="Failed to create account",
                data={"email": member.email},
            ) from exc
        finally:
            db.refresh(account)
            db.refresh(member_account)
            db.refresh(invite)

    return {
        "id": member_account.id,
        "name": member.name,
        "email": member.email,
        "role": role.role.name,
        "organization": organization.name,
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
        db.query(InviteMember)
        .filter(InviteMember.invite_token == invite_token)
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

    role = (
        db.query(OrganizationRole)
        .join(
            OrganizationMember,
            OrganizationMember.organization_role_id == OrganizationRole.id,
        )
        .filter(OrganizationMember.account_id == member.account_id)
        .filter(OrganizationMember.organization_id == member.organization_id)
        .first()
    )

    # Accept invite
    try:
        member.is_accepted = True
        member.status = "accepted"
        member.accepted_invite_date = datetime.utcnow()
        member.updated_at = datetime.utcnow()
        db.commit()
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
        "role": role.role.name,
        "organization": member.organization.name,
        "invite_token": member.invite_token,
        "is_accepted": member.is_accepted,
    }


def suspend_member(
    db: Session,
    organization_id: str,
    member_id: str,
) -> Dict[str, Any]:
    """Suspend and unsuspends a member.

    Args:
        db (Session): Database session
        organization_id (str): Organization ID
        member_id (str): Member ID

    Raises:
        CustomException: If organization does not exist
        CustomException: If member does not exist
        CustomException: If member is already suspended
        CustomException: If member is not accepted
        CustomException: If failed to suspend member

    Returns:
        dict: Member details
    """
    # Check if organization exists
    organization = (
        db.query(Organization)
        .filter(Organization.id == organization_id)
        .first()
    )
    if not organization:
        raise CustomException(
            status_code=404,
            message="Organization not found",
            data={"organization_id": organization_id},
        )

    # Check if member exists
    member = (
        db.query(OrganizationMember)
        .filter(OrganizationMember.organization_id == organization_id)
        .filter(OrganizationMember.id == member_id)
        .first()
    )

    invite_instance = (
        db.query(InviteMember)
        .filter(InviteMember.organization_id == organization_id)
        .filter(InviteMember.account_id == member.account_id)
        .first()
    )
    if not member:
        raise CustomException(
            status_code=404,
            message="Member not found",
            data={"member_id": member_id},
        )

    # Check if member is accepted
    if not invite_instance.is_accepted:
        raise CustomException(
            status_code=400,
            message="Member has not accepted invite",
            data={"member_id": member_id},
        )

    # Suspend member
    try:
        member.is_suspended = not member.is_suspended
        db.commit()
        db.refresh(member)
    except Exception as exc:
        raise CustomException(
            status_code=500,
            message="Failed to suspend member",
            data={"member_id": member_id},
        ) from exc

    return {
        "id": member.id,
        "name": f"{member.account.first_name} {member.account.last_name}",
        "email": member.account.email,
        "role": member.member_role.role.name,
        "is_suspended": member.is_suspended,
    }


def delete_organization(db: Session, organization_id: str) -> Dict[str, Any]:
    """Delete an organization.

    Args:
        db (Session): Database session
        organization_id (str): Organization ID

    Raises:
        CustomException: If organization does not exist

    Returns:
        dict: Organization details
    """
    organization: Organization = check_organization_exists(
        db, organization_id=organization_id
    )
    if not organization:
        raise CustomException(
            status_code=404,
            message="Organization not found",
            data={"organization_id": organization_id},
        )

    try:
        db.delete(organization)

        db.commit()

    except Exception as exc:
        raise CustomException(
            status_code=500,
            message="Failed to delete organization",
            data={"organization_id": organization.id},
        ) from exc

    return "success"


def check_organization_exists(
    db: Session, name: str | None = None, organization_id: str | None = None
) -> Organization:
    """Check if an organization name exists."""
    if organization_id:
        return (
            db.query(Organization)
            .filter(Organization.id == organization_id)
            .first()
        )
    return db.query(Organization).filter(Organization.name == name).first()


def check_organization_member_exists(
    organization_id: str, account_id: str, db: Session
) -> Any:
    """Check if an organization member exists."""
    return (
        db.query(OrganizationMember)
        .filter(
            OrganizationMember.organization_id == organization_id,
            OrganizationMember.account_id == account_id,
        )
        .first()
    )


def check_organization_member_is_admin(
    organization_id: str, account_id: str, db: Session
) -> Any:
    """Check if an organization member is an admin."""
    return (
        db.query(OrganizationMember, Organization)
        .filter(
            OrganizationMember.organization_id == organization_id,
            OrganizationMember.account_id == account_id,
            Organization.owner == account_id,
        )
        .first()
    )
