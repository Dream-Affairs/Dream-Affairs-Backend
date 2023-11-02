"""This file contains the database connection and session."""
# database.py
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


def get_db_engine() -> Engine:
    """
    Get db engine:
        This function returns the database engine.
        it create a sqlite database if not connected to a
        postgresql database.

    Returns:
        create_engine: The database engine.
    """
    db_type = settings.DB_TYPE
    db_name = settings.DB_NAME
    db_user = settings.DB_USER
    db_password = settings.DB_PASSWORD
    db_host = settings.DB_HOST
    db_port = settings.DB_PORT

    if db_type == "postgresql":
        database_url = f"postgresql://{db_user}:{db_password}"\
                f"@{db_host}:{db_port}/{db_name}"

        return create_engine(database_url)

    if db_type == "sqlite":
        database_url = "sqlite:///./database.db"
        return create_engine(
            database_url, connect_args={"check_same_thread": False}
        )

    raise ValueError("Database type not supported")


db_engine = get_db_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)

Base = declarative_base()


def create_database() -> Any:
    """
    Create database:
        This function creates the database if it is not present and
        creates all the tables in the database. It returns the
        database engine.

        This function is called in the main.py file. If a LOCAL
        environment variable is set to True
    """
    print("Connected to the database")
    return Base.metadata.create_all(bind=db_engine)


def get_db() -> object:
    """
    Get db:
        This function returns the database session.
        It is used in the in any router file to get
        the database session.
    """
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()
    return database


def get_db_unyield() -> object:
    """
    Get db unyield:
        This function returns the database session.
        It is used mainly for writing to the database externally
        from the entire application.
    """
    # create_database()
    database = SessionLocal()
    return database
