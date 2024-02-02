"""This module contains the services for the tables and tags."""
from sqlalchemy.orm import Session

from app.api.models.organization_models import (
    OrganizationTable,
    OrganizationTag,
)
from app.api.responses.custom_responses import CustomException, CustomResponse
from app.api.schemas.table_tag_schemas import (
    TableResponse,
    TableSchema,
    TagResponse,
    TagSchema,
    TagType,
)


def get_all_organization_tables(
    organization_id: str,
    db: Session,
) -> CustomResponse:
    """
    get_all_organization_tables:
        This method is used to get all the tables of an organization.

    Args:
        organization_id: This is the ID of the organization.
        db: This is the SQLAlchemy Session object.

    Returns:
        List[TableResponse]: This is the list of tables.

    Raises:
        CustomException: This is raised if an error occurs while getting all\
           the tables.
    """
    try:
        tables_tag = (
            db.query(OrganizationTable)
            .filter_by(organization_id=organization_id)
            .all()
        )
        return CustomResponse(
            data=[
                TableResponse(
                    id=table.id,
                    name=table.name,
                    assigned_table_count=table.assigned_table_count,
                    available_table_count=table.available_table_count,
                    total_available_seats=table.total_available_seats,
                ).model_dump()
                for table in tables_tag
            ],
            message="Get all tables tag successfully",
            status_code=200,
        )
    except Exception as e:
        print(e)
        raise CustomException(
            message="Get all tables tag failed", status_code=500
        ) from e


def get_all_organization_tags(
    organization_id: str,
    tag_type: TagType,
    db: Session,
) -> CustomResponse:
    """
    get_all_organization_tags:
        This method is used to get all the tags of an organization.

    Args:
        organization_id: This is the ID of the organization.
        type: This is the type of the tag.
        db: This is the SQLAlchemy Session object.

    Returns:
        List[TagResponse]: This is the list of tags.

    Raises:
        CustomException: This is raised if an error occurs\
           while getting all the tags.
    """
    try:
        tags = (
            db.query(OrganizationTag)
            .filter(
                OrganizationTag.organization_id == organization_id,
                OrganizationTag.tag_type == tag_type,
            )
            .all()
        )
        return CustomResponse(
            data=[
                TagResponse(
                    id=tag.id,
                    name=tag.name,
                    description=tag.description,
                    tag_type=tag.tag_type,
                ).model_dump()
                for tag in tags
            ],
            message="Get all tags successfully",
            status_code=200,
        )
    except Exception as e:
        print(e)
        raise CustomException(
            message="Get all tags failed", status_code=500
        ) from e


def add_organization_table(
    organization_id: str,
    table_instance: TableSchema,
    db: Session,
) -> CustomResponse:
    """
    add_organization_table:
        This method is used to add a table to an organization.

    Args:
        organization_id: This is the ID of the organization.
        table_instance: This is the table schema.
        db: This is the SQLAlchemy Session object.

    Returns:
        TableResponse: This is the table that was added.

    Raises:
        CustomException: This is raised if an error occurs\
            while adding the table.
    """
    try:
        table = OrganizationTable(
            organization_id=organization_id,
            name=table_instance.name,
            assigned_table_count=table_instance.assigned_table_count,
            available_table_count=table_instance.available_table_count,
            total_available_seats=table_instance.total_available_seats,
        )
        db.add(table)
        db.commit()
        db.refresh(table)
        return CustomResponse(
            data=TableResponse(
                id=table.id,
                name=table.name,
                assigned_table_count=table.assigned_table_count,
                available_table_count=table.available_table_count,
                total_available_seats=table.total_available_seats,
            ).model_dump(),
            message="Add table successfully",
            status_code=200,
        )
    except Exception as e:
        raise CustomException(
            message="Add table failed", status_code=500
        ) from e


def add_organization_tag(
    organization_id: str,
    tag_instance: TagSchema,
    db: Session,
) -> CustomResponse:
    """
    add_organization_tag:
        This method is used to add a tag to an organization.

    Args:
        organization_id: This is the ID of the organization.
        tag_instance: This is the tag schema.
        db: This is the SQLAlchemy Session object.

    Returns:
        TagResponse: This is the tag that was added.

    Raises:
        CustomException: This is raised if an error occurs\
            while adding the tag.
    """
    try:
        tag = OrganizationTag(
            organization_id=organization_id,
            name=tag_instance.name,
            description=tag_instance.description,
            tag_type=tag_instance.tag_type,
        )
        db.add(tag)
        db.commit()
        db.refresh(tag)
        print(tag.id, tag.name, tag.description, tag.tag_type)
        return CustomResponse(
            data=TagResponse(
                id=tag.id,
                name=tag.name,
                description=tag.description,
                tag_type=tag.tag_type,
            ).model_dump(),
            message="Add tag successfully",
            status_code=200,
        )
    except Exception as e:
        print(e)
        raise CustomException(message="Add tag failed", status_code=500) from e


def delete_organization_table(
    organization_id: str,
    table_id: str,
    db: Session,
) -> CustomResponse:
    """
    delete_organization_table:
        This method is used to delete a table from an organization.

    Args:
        organization_id: This is the ID of the organization.
        table_id: This is the ID of the table.
        db: This is the SQLAlchemy Session object.

    Returns:
        CustomResponse: This is the response after deleting the table.

    Raises:
        CustomException: This is raised if an error\
            occurs while deleting the table.
    """
    try:
        table = (
            db.query(OrganizationTable)
            .filter(
                OrganizationTable.id == table_id,
                OrganizationTable.organization_id == organization_id,
            )
            .first()
        )
        if table is None:
            raise CustomException(message="Table not found", status_code=404)
        db.delete(table)
        db.commit()
        return CustomResponse(
            data=None,
            message="Delete table successfully",
            status_code=200,
        )
    except Exception as e:
        raise CustomException(
            message="Delete table failed", status_code=500
        ) from e


def delete_organization_tag(
    organization_id: str,
    tag_id: str,
    db: Session,
) -> CustomResponse:
    """
    delete_organization_tag:
        This method is used to delete a tag from an organization.

    Args:
        organization_id: This is the ID of the organization.
        tag_id: This is the ID of the tag.
        db: This is the SQLAlchemy Session object.

    Returns:
        CustomResponse: This is the response after deleting the tag.

    Raises:
        CustomException: This is raised if an error\
            occurs while deleting the tag.
    """
    try:
        tag = (
            db.query(OrganizationTag)
            .filter(
                OrganizationTag.id == tag_id,
                OrganizationTag.organization_id == organization_id,
            )
            .first()
        )
        if tag is None:
            raise CustomException(message="Tag not found", status_code=404)
        db.delete(tag)
        db.commit()
        return CustomResponse(
            data=None,
            message="Delete tag successfully",
            status_code=200,
        )
    except Exception as e:
        raise CustomException(
            message="Delete tag failed", status_code=500
        ) from e
