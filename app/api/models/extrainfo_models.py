"""This file contains the models for the Extrainfo table."""
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.sql import func

from app.database.connection import Base


class Extrainfo(Base):  # type: ignore
    """
    Extrainfo model:
      This table contains the Extrainfo for the organization.

    Attributes:
      id (str): The id of the Extrainfo.
      rel_id (str): The id of the object to which the Extrainfo belongs.
      model_type (str): The model_type of the Extrainfo.
      key (str): The key of the Extrainfo.
      value (str): The value of the Extrainfo.
      value_dt (str): The value_dt of the Extrainfo.
      description (str): The description of the Extrainfo.
      is_primary (str): The is_primary of the Extrainfo.
      is_deleted (str): The is_deleted of the Extrainfo.
      date_created (str): The date_created of the Extrainfo.
      last_updated (str): The last_updated of the Extrainfo.
      date_created_db (str): The date_created_db of the Extrainfo.
      last_updated_db (str): The last_updated_db of the Extrainfo.


    """

    __tablename__ = "extrainfo"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    rel_id = Column(String(255))
    model_type = Column(String(255))
    key = Column(String(255), nullable=False)
    value = Column(String(255), default="")
    value_dt = Column(DateTime, default=None)
    description = Column(String(255), default="")
    is_primary = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    date_created = Column(DateTime, server_default=func.now())
    last_updated = Column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
