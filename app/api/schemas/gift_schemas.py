"""This module defines Pydantic schemas for registy/gift."""

from typing import Optional

from pydantic import BaseModel


class GiftSchema(BaseModel):  # type: ignore
    """Represents the base schema for a gift."""

    title: str
    product_unit_price: float
    product_quantity: Optional[int] = None
    currency: str
    gift_type: str
    product_image_url: str
    description: Optional[str] = None


class AddProductGift(GiftSchema):
    """Represents the schema for adding product gift."""

    product_url: str

    class Config:
        """Repersents the config model for this Schema
        Aim:
            Specify how I want my schema to react with the data I pass
        orm_mode:
            Converts sqlalchemy models to dictionarits for smooth parsing"""

        orm_mode = True
        from_attributes = True
