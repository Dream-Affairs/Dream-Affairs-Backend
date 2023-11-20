"""This module contains the database model for the email table."""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship

from app.database.connection import Base


class TrackEmail(Base):  # type: ignore
    """This table is used to track all types of emails sent from the
    application."""

    __tablename__ = "track_email"

    id = Column(String, primary_key=True, default=uuid4().hex)
    email_id = Column(String)
    organization_id = Column(String, ForeignKey("organization.id"))
    unique_id = Column(String, primary_key=True, default=uuid4().hex)
    subject = Column(String)
    recipient = Column(String)
    template = Column(String)
    status = Column(
        ENUM("sent", "failed", name="email_status"), default="sent"
    )
    reason = Column(String)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="track_email")
