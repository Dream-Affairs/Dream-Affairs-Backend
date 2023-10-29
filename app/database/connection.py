"""This file contains the database connection and session."""
# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings


def get_db_engine():
    """
    Get db engine:
        This function returns the database engine based on the database type.
        If the database type is sqlite then it returns the
        sqlite engine else it returns the postgresql engine.
        it also checks if the database type is sqlite then
        it checks if the database is present or not.
        If the database is not present then it creates the database.
        It's parameters are taken from the config.py file which
        is gotten from the environment variables.

    Parameters:
    - db_type: This is the type of the database used (sqlite, postgresql).
    - db_name: This is the name of the database.
    - db_user: This is the username of the database.
    - db_password: This is the password of the database.
    - db_host: This is the hostname of the database.
    - db_port: This is the port of the database.

    """
    db_type = settings.DB_TYPE
    db_name = settings.DB_NAME
    db_user = settings.DB_USER
    db_password = settings.DB_PASSWORD
    db_host = settings.DB_HOST
    db_port = settings.DB_PORT

    if db_type == "postgresql":
        database_url = f"postgresql://{db_user}:{db_password}\
              @{db_host}:{db_port}/{db_name}"
    else:
        database_url = "sqlite:///./database.db"
        return create_engine(
            database_url, connect_args={"check_same_thread": False}
        )

    return create_engine(database_url)


db_engine = get_db_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)

Base = declarative_base()


def create_database():
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


def get_db():
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


def get_db_unyield():
    """
    Get db unyield:
        This function returns the database session.
        It is used mainly for writing to the database externally
        from the entire application.
    """
    # create_database()
    database = SessionLocal()
    return database
