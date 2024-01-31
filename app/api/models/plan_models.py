# """This module contains the models for the plan table."""
# from datetime import datetime
# from uuid import uuid4

# from sqlalchemy import (
#     Boolean,
#     Column,
#     DateTime,
#     Float,
#     ForeignKey,
#     Index,
#     String,
# )
# from sqlalchemy.dialects.postgresql import ENUM
# from sqlalchemy.orm import Session, relationship

# from app.database.connection import Base


# class Plan(Base):  # type: ignore
#     """
#     Plan:
#         This class is used to create the plan table.

#     Args:
#         Base: This is the base class from which all the models inherit.

#     attributes:
#         id: This is the primary key of the table.
#         name: This is the name of the plan.
#         description: This is the description of the plan.
#         is_active: This is the boolean value which tells whether \
#             the plan is active or not.
#         is_deleted: This is the boolean value which tells whether \
#             the plan is deleted or not.
#         created_at: This is the date and time when the plan was created.
#         updated_at: This is the date and time when the plan was updated.
#         deleted_at: This is the date and time when the plan was deleted.

#     Relationships:
#         organizations: This is the relationship between the plan and \
#             organization table.
#     """

#     __tablename__ = "plan"
#     id = Column(String, primary_key=True, default=uuid4().hex)
#     name = Column(String, nullable=False)
#     other_name = Column(String, nullable=False)
#     price = Column(Float(2), nullable=False)
#     description = Column(String)
#     is_active = Column(Boolean, default=True)
#     is_deleted = Column(Boolean, default=False)

#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow)

#     # organizations = relationship("OrganizationPlan", back_populates="plan")

#     @classmethod
#     def create_default_plans(cls, db: Session) -> None:
#         """
#         create_default_plans:
#             This method is used to create the default plans.

#         Args:
#             db: This is the SQLAlchemy Session object.
#         """
#         default_plans = [
#             {
#                 "name": "Free Plan",
#                 "other_name": "basic",
#                 "price": 0.00,
#                 "description": "Basic Event Management Plan",
#             },
#             {
#                 "name": "Pro Plan",
#                 "other_name": "premium",
#                 "price": 10.00,
#                 "description": "Conmprehensive Event Suite",
#             },
#             {
#                 "name": "Core Plan",
#                 "other_name": "core",
#                 "price": 50.00,
#                 "description": "Advanced Planning Features",
#             },
#         ]

#         print("Creating default plans...")
#         for plan in default_plans:
#             if cls.find_by_name(db=db, name=plan["name"]):
#                 continue
#             plan_obj = Plan(**plan, id=uuid4().hex)
#             db.add(plan_obj)
#             db.commit()
#             db.refresh(plan_obj)

#     @classmethod
#     def find_by_name(cls, db: Session, name: str) -> "Plan":
#         """
#         find_by_name:
#             This method is used to get a plan by its name.

#         Args:
#             db: This is the SQLAlchemy Session object.
#             name: This is the name of the plan.

#         Returns:
#             Plan: This is the plan object.
#         """
#         return db.query(cls).filter_by(name=name).first()
