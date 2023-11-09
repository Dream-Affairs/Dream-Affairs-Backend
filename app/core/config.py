"""This module is used for configuration of the application's settings."""
from decouple import config


class Settings:
    """
    Settings:
        This class is used to get the environment variables
        from the .env file.
    """

    DB_TYPE = config("DB_TYPE", default="sqlite")
    DB_NAME = config("DB_NAME", default="database")
    DB_USER = config("DB_USER", default="root")
    DB_PASSWORD = config("DB_PASSWORD", default="root")
    DB_HOST = config("DB_HOST", default="localhost")
    DB_PORT = config("DB_PORT", default="5432")
    ENVIRONMENT = config("ENVIRONMENT", default="development")
    AUTH_SECRET_KEY = config("AUTH_SECRET_KEY")
    HASH_ALGORITHM = config("HASH_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES = config(
        "ACCESS_TOKEN_EXPIRE_MINUTES", default=30
    )
    PRD_SENTRY_DSN = config("PRD_SENTRY_DSN", default="")
    DEV_SENTRY_DSN = config("DEV_SENTRY_DSN", default="")

    EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
    EMAIL_PORT = config("EMAIL_PORT", default="587")
    EMAIL_NAME = config("EMAIL_NAME", default="admin")
    EMAIL_PASSWORD = config("EMAIL_PASSWORD", default="password")
    EMAIL_ADDRESS = config("EMAIL_ADDRESS", default="")


settings = Settings()
