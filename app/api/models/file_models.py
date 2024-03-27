"""This module contains the file models."""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column
from sqlalchemy.types import Boolean, DateTime, Integer, String

from app.database.connection import Base


class File(Base):
    """This class represents the file model."""

    __tablename__ = "files"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    file_name = Column(
        String(255),
    )
    file_for = Column(String(255))
    file_type = Column(ENUM("csv", "xlsx", name="file_type"), default="csv")
    file_size = Column(String(255))
    organization_id = Column(String(255), ForeignKey("organization.id"))
    user_id = Column(String(255))
    request_type = Column(ENUM("import", "export", name="request_type"))
    is_deleted = Column(Boolean, default=False)
    date_created = Column(DateTime, default=datetime.now())
    last_updated = Column(DateTime, default=datetime.now())

    organization_info = relationship(
        "Organization", backref="files", lazy="joined"
    )
    import_info = relationship(
        "FileImports", back_populates="file", lazy="joined"
    )
    # export_info = relationship("FileExports", backref="files", lazy="joined")


class FileImports(Base):
    """This class represents the file import model."""

    __tablename__ = "imports"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    file_id = Column(String(255), ForeignKey("files.id"))
    current_line = Column(Integer, default=0)
    total_line = Column(Integer)
    in_progress = Column(Boolean, default=False)
    user_id = Column(String(255))
    is_deleted = Column(Boolean, default=False)
    date_created = Column(DateTime, default=datetime.now())
    last_updated = Column(DateTime, default=datetime.now())

    file = relationship("File", back_populates="import_info", lazy="joined")
    failed_imports = relationship(
        "FailedFileImports", backref="failed_import", lazy="joined"
    )


class FailedFileImports(Base):
    """This class represents the failed file import model."""

    __tablename__ = "failed_imports"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    error = Column(String(255), default=None)
    import_id = Column(String(255), ForeignKey("imports.id"))
    line = Column(String(50), default=None)
    is_deleted = Column(Boolean, default=False)
    date_created = Column(DateTime, default=datetime.now())
    last_updated = Column(DateTime, default=datetime.now())


# class FileExports(Base):
#     __tablename__= "Exports"
#     id = Column(String(255),primary_key=True,index=True,default=uuid4().hex)
#     organization_id = Column(String,
#     ForeignKey("organization.id", ondelete="CASCADE"), nullable=False)
#     event_name = Column(String(255),)
#     file_name = Column(String(255), unique=True)
#     file_id = Column(String(255), ForeignKey("files.id"))
#     user_id = Column(String(255))
#     report_type = Column(String(255))
#     settings = Column(JSON())
#     last_id = Column(String(255))
#     current_line = Column(String(255))
#     totat_count = Column(String(255))
#     is_deleted= Column(Boolean, default=False)
#     date_created = Column(DateTime, default=datetime.now())
#     last_updated = Column(DateTime, default=datetime.now())
