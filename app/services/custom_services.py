""" This module contains the custom services for the application. """


def model_to_dict(models):
    """Converts a list of SQLAlchemy models to a list of dictionaries

    Args:
        models (list): List of SQLAlchemy models

    Returns:
        list: A list of dictionary representations of the models
    """
    list = [
        {
            column.name: getattr(model, column.name)
            for column in model.__table__.columns
        }
        for model in models
    ]

    return list
