"""This module contains services for the organization model."""
from typing import Any

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.models.organization_models import Organization, OrganizationMember


def check_organization_exists(
    db: Session, name: str | None = None, organization_id: str | None = None
) -> Any:
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


class OrganizationSchema(BaseModel):
    """Data model for an organization.

    Attributes:
        name (str): The name of the organization.
        owner (str): The ID of the owner of the organization.
        id (str): The id of
    """

    id: str
    name: str
    account_id: str
    organization_id: str
