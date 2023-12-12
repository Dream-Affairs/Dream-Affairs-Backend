"""This file contains the models for the budget and expenditure tables."""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database.connection import Base


class Budget(Base):  # type: ignore
    """
    Budget model:
      This table contains the budget for the organization.

    Attributes:
      id (str): The id of the budget.
      organization_id (str): The id of the organization to which \
        the budget belongs.
      title (str): The title of the budget.
      currency (str): The currency of the budget.
      amount (int): The amount of the budget.
      description (str): The description of the budget.

      created_at (datetime): The date and time when the budget was \
        created.
      updated_at (datetime): The date and time when the budget was \
        last updated.

      organization (object): The organization to which the budget \
        belongs.
      expenditures (list): The list of expenditures associated with \
        the budget.
    """

    __tablename__ = "budget"
    id = Column(String, primary_key=True, default=uuid4().hex)
    organization_id = Column(
        String,
        ForeignKey("organization.id", ondelete="CASCADE"),
        nullable=False,
    )
    title = Column(String, nullable=False)
    currency = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    description = Column(
        String,
    )

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship(
        "Organization", back_populates="budget", lazy="joined"
    )
    expenditures = relationship(
        "Expenditure",
        back_populates="budget",
        lazy="joined",
        cascade="all,delete",
    )


class Expenditure(Base):  # type: ignore
    """
    Expenditure model:
      This table contains the expenditure for the organization.

    Attributes:
      id (str): The id of the expenditure.
      organization_id (str): The id of the organization to which the \
        expenditure belongs.
      title (str): The title of the expenditure.
      currency (str): The currency of the expenditure.
      amount (int): The amount of the expenditure.
      description (str): The description of the expenditure.

      created_at (datetime): The date and time when the expenditure \
        was created.
      updated_at (datetime): The date and time when the expenditure \
        was last updated.

      organization_budget (object): The budget to which the \
        expenditure belongs.
    """

    __tablename__ = "expenditure"
    id = Column(String, primary_key=True, default=uuid4().hex)
    budget_id = Column(String, ForeignKey("budget.id"), nullable=False)
    title = Column(String, nullable=False)
    currency = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    description = Column(
        String,
    )

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    budget = relationship(
        "Budget", back_populates="expenditures", lazy="joined"
    )
