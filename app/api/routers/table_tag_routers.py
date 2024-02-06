"""This module contains the FastAPI routers for the table_tag endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.middlewares.authorization import Authorize, is_org_authorized
from app.api.schemas.table_tag_schemas import TableSchema, TagSchema, TagType
from app.database.connection import get_db
from app.services.tables_tag_services import (
    add_organization_table,
    add_organization_tag,
    delete_organization_table,
    delete_organization_tag,
    get_all_organization_tables,
    get_all_organization_tags,
)

router = APIRouter(
    prefix="/table_tag",
    tags=["Table_Tag"],
)


@router.get("/tables", tags=["Tables"])
async def get_all_tables(
    db: Session = Depends(get_db),
    auth: Authorize = Depends(is_org_authorized),
):
    """
    get_all_tables:
        This method is used to get all the tables of  an organization.

    Args:
        db: This is the SQLAlchemy Session object.
        organization_id: This is the ID of the organization.

    Returns:
        List[TableResponse]: This is the list of tables.
    """
    return get_all_organization_tables(auth.member.organization_id, db)


@router.get("/tags", tags=["Tags"])
async def get_all_tags(
    tag_type: TagType,
    db: Session = Depends(get_db),
    auth: Authorize = Depends(is_org_authorized),
):
    """
    get_all_tags:
        This method is used to get all the tags of  an organization.

    Args:
        db: This is the SQLAlchemy Session object.
        organization_id: This is the ID of the organization.

    Returns:
        List[TagResponse]: This is the list of tags.
    """
    return get_all_organization_tags(auth.member.organization_id, tag_type, db)


@router.post("/table", tags=["Tables"])
async def create_table(
    table: TableSchema,
    db: Session = Depends(get_db),
    auth: Authorize = Depends(is_org_authorized),
):
    """
    create_table:
        This method is used to create a table.

    Args:
        db: This is the SQLAlchemy Session object.
        tableSchema: This is the table schema.
        organization_id: This is the ID of the organization.

    Returns:
        TableResponse: This is the table that was created.
    """
    return add_organization_table(auth.member.organization_id, table, db)


@router.post("/tag", tags=["Tags"])
async def create_tag(
    tag: TagSchema,
    db: Session = Depends(get_db),
    auth: Authorize = Depends(is_org_authorized),
):
    """
    create_tag:
        This method is used to create a tag.

    Args:
        db: This is the SQLAlchemy Session object.
        tagSchema: This is the tag schema.
        organization_id: This is the ID of the organization.

    Returns:
        TagResponse: This is the tag that was created.
    """
    return add_organization_tag(auth.member.organization_id, tag, db)


@router.delete("/table/{table_id}", tags=["Tables"])
async def delete_table(
    table_id: str,
    db: Session = Depends(get_db),
    auth: Authorize = Depends(is_org_authorized),
):
    """
    delete_table:
        This method is used to delete a table.

    Args:
        db: This is the SQLAlchemy Session object.
        table_id: This is the ID of the table.
        organization_id: This is the ID of the organization.

    Returns:
        TableResponse: This is the table that was deleted.
    """
    return delete_organization_table(auth.member.organization_id, table_id, db)


@router.delete("/tag/{tag_id}", tags=["Tags"])
async def delete_tag(
    tag_id: str,
    db: Session = Depends(get_db),
    auth: Authorize = Depends(is_org_authorized),
):
    """
    delete_tag:
        This method is used to delete a tag.

    Args:
        db: This is the SQLAlchemy Session object.
        tag_id: This is the ID of the tag.
        organization_id: This is the ID of the organization.
    """
    return delete_organization_tag(auth.member.organization_id, tag_id, db)
