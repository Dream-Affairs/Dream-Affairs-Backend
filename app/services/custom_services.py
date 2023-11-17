""" This module contains the custom services for the application. """
from datetime import datetime

def model_to_dict(models):
    """Converts a list of SQLAlchemy models to a list of dictionaries

    Args:
        models (list): List of SQLAlchemy models

    Returns:
        list: A list of dictionary representations of the models
    """
    def convert_datetime(value):
        """Converts datetime objects to ISO format"""
        if isinstance(value, datetime):
            return value.isoformat()
        return value

    result_list = [
        {
            column.name: convert_datetime(getattr(model, column.name))
            for column in model.__table__.columns
        }
        for model in models
    ]

    return result_list
