"""This module contains services for the organization model."""
from typing import Any

from sqlalchemy.orm import Session

from app.api.models.organization_models import Organization, OrganizationMember


def check_organization_name_exists(name: str, db: Session) -> Any:
    """Check if an organization name exists."""
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
