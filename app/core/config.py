"""This module is used for configuration of the application's settings."""

import logging
import logging.config
import sys

from decouple import config


class Settings:
    """
    Settings:
        This class is used to get the environment variables
        from the .env file.
    """

    TEMPLATE_DIR = config("TEMPLATE_DIR", default="app/templates")
    DB_TYPE = config("DB_TYPE", default="sqlite")
    DB_NAME = config("DB_NAME", default="database")
    DB_USER = config("DB_USER", default="root")
    DB_PASSWORD = config("DB_PASSWORD", default="root")
    DB_HOST = config("DB_HOST", default="localhost")
    DB_PORT = config("DB_PORT", default="5432")
    ENVIRONMENT = config("ENVIRONMENT", default="")
    AUTH_SECRET_KEY = config("AUTH_SECRET_KEY", cast=str)
    HASH_ALGORITHM = config("HASH_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES = config(
        "ACCESS_TOKEN_EXPIRE_MINUTES", default=1000, cast=int
    )
    PRD_SENTRY_DSN = config("PRD_SENTRY_DSN", default="")
    DEV_SENTRY_DSN = config("DEV_SENTRY_DSN", default="")

    EMAIL_API_URI = config(
        "EMAIL_API_URI", default="https://api.elasticemail.com/v2", cast=str
    )
    EMAIL_SENDER = config(
        "EMAIL_SENDER", default="dream-affairs@owoborodeseye.online"
    )
    EMAIL_NAME = config("EMAIL_NAME", default="admin")
    EMAIL_API_KEY = config("EMAIL_API_KEY", default="")
    EMAIL_REQUEST_TIMEOUT = config("EMAIL_REQUEST_TIMEOUT", default=10)

    CLOUDINARY_CLOUD_NAME = config("CLOUDINARY_CLOUD_NAME", default="")
    CLOUDINARY_API_KEY = config("CLOUDINARY_API_KEY", default="")
    CLOUDINARY_API_SECRET = config("CLOUDINARY_API_SECRET", default="")

    GOOGLE_CLIENT_ID = config("GOOGLE_CLIENT_ID", default="")
    GOOGLE_CLIENT_SECRET = config("GOOGLE_CLIENT_SECRET", default="")
    GOOGLE_REDIRECT_URI = config("GOOGLE_REDIRECT_URI", default="")

    FRONT_END_HOST = config(
        "FRONT_END_HOST",
        default="https://dream-affairs-frontend-dev.vercel.app",
    )

    PLAN_BASIC_PRICE = config("PLAN_BASIC_PRICE", default=0.00, cast=float)
    PLAN_PREMIUM_PRICE = config(
        "PLAN_PREMIUM_PRICE", default=10.00, cast=float
    )
    PLAN_CORE_PRICE = config("PLAN_CORE_PRICE", default=50.00, cast=float)

    LOG_FILE = config("LOG_FILE", default="app.log")


settings = Settings()

logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(levelname)s \
            %(name)s %(module)s %(funcName)s %(lineno)d %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "formatter": "json",
        },
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": settings.LOG_FILE,
            "formatter": "json",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["file"],
        "propagate": True,
        "formatter": "json",
    },
    "loggers": {
        "uvicorn": {
            "level": "INFO",
            "handlers": ["file"],
            "propagate": True,
            "formatter": "json",
        },
        "fastapi": {
            "level": "INFO",
            "handlers": ["file"],
            "propagate": True,
            "formatter": "json",
        },
    },
}

logging.config.dictConfig(logging_config)
