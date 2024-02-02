"""Schemas for table tags."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel


class TagType(str, Enum):
    """Represents the type of a tag."""

    DIETARY = "dietary"
    GUEST = "guest"


class BaseData(BaseModel):
    """Base data schema."""

    name: str
    description: Optional[str] = None


class TableSchema(BaseData):
    """Data schema for a table.

    Attributes:
      id (Optional[str]): The ID of the table.
      name (str): The name of the table.
      description (str): The description of the table.
      assigned_table_count (int): The number of assigned tables.
    """

    assigned_table_count: int = 0
    available_table_count: int = 0
    total_available_seats: int = 0


class TableResponse(TableSchema):
    """Data schema for a table response.

    Attributes:
      id (Optional[str]): The ID of the table.
      name (str): The name of the table.
      description (str): The description of the table.
      assigned_table_count (int): The number of assigned tables.
      available_table_count (int): The number of available tables.
      total_available_seats (int): The total number of available seats.
    """

    id: str


class TagSchema(BaseData):
    """Data schema for a tag.

    Attributes:
      id (Optional[str]): The ID of the tag.
      name (str): The name of the tag.
      description (str): The description of the tag.
      tag_type (TagType): The type of the tag.
    """

    tag_type: TagType


class TagResponse(TagSchema):
    """Data schema for a tag response.

    Attributes:
      id (Optional[str]): The ID of the tag.
      name (str): The name of the tag.
      description (str): The description of the tag.
      tag_type (TagType): The type of the tag.
      table_count (int): The number of tables with this tag.
    """

    id: str
