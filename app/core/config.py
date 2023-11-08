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
    PRD_SENTRY_DSN = config("PRD_SENTRY_DSN", default="")
    DEV_SENTRY_DSN = config("DEV_SENTRY_DSN", default="")


settings = Settings()
