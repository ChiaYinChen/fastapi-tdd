"""Handles application logging configuration.

This module sets up the logging formatters, handlers, and loggers
for the application using Python's `logging` library and `colorlog`
for colored output in debug mode. It defines the logging structure
and provides a function to apply this configuration.

Attributes:
    LOG_LEVEL (str): The effective logging level for the application,
        determined by application settings (DEBUG mode or explicit LOG_LEVEL).
    LOGGING_CONFIG (dict[str, Any]): The dictionary-based configuration
        for Python's logging system.
"""
import logging.config
from typing import Any

from ..constants.logging import LogLevel
from ..core.config import settings

LOG_LEVEL = str(LogLevel.DEBUG) if settings.DEBUG else str(settings.LOG_LEVEL)

LOGGING_CONFIG: dict[str, Any] = {  # noqa: WPS407
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "colored": {
            "()": "colorlog.ColoredFormatter",
            "format": (
                "%(log_color)s%(levelname)-5s%(reset)s "
                "%(yellow)s[%(asctime)s]%(reset)s"
                "%(white)s %(name)s %(funcName)s "
                "%(bold_purple)s:%(lineno)d%(reset)s "
                "%(log_color)s%(message)s%(reset)s"
            ),
            "datefmt": "%y-%m-%d %H:%M:%S",
            "log_colors": {
                "DEBUG": "blue",
                "INFO": "bold_cyan",
                "WARNING": "red",
                "ERROR": "bg_bold_red",
                "CRITICAL": "red,bg_white",
            },
        },
        "simple": {
            "format": ("%(levelname)-5s [%(asctime)s] %(name)s %(funcName)s :%(lineno)d %(message)s"),
            "datefmt": "%y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "default": {
            "level": LOG_LEVEL,
            "class": "logging.StreamHandler",
            "formatter": "colored" if settings.DEBUG else "simple",
        },
    },
    "loggers": {
        "": {
            "handlers": ["default"],
            "level": LOG_LEVEL,
            "propagate": True,
        },
        "uvicorn.error": {
            "handlers": ["default"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["default"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
    },
}


def configure_logging() -> None:
    """Configures the application's logging.

    Applies the logging configuration defined in `LOGGING_CONFIG` using
    `logging.config.dictConfig`. This function should typically be called
    once at application startup.
    """
    logging.config.dictConfig(LOGGING_CONFIG)
