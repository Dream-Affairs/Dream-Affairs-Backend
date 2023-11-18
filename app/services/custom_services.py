"""This module contains the custom services for the application."""
from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy.ext.declarative import DeclarativeMeta


def model_to_dict(models: List[DeclarativeMeta]) -> List[Dict[str, Any]]:
    """Converts a list of SQLAlchemy models to a list of dictionaries.

    Args:
        models (List[DeclarativeMeta]): List of SQLAlchemy models

    Returns:
        List[Dict[str, Any]]: A dictionary representations of the models
    """

    def convert_datetime(value: Any) -> Any:
        """Converts datetime objects to ISO format."""
        if isinstance(value, datetime):
            return value.isoformat()
        return value

    result_list: List[Dict[str, Any]] = [
        {
            column.name: convert_datetime(getattr(model, column.name))
            for column in model.__table__.columns
        }
        for model in models
    ]

    return result_list
