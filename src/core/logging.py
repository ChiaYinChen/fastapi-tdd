import logging.config
from typing import Any

from ..constants.logging import LogLevel
from ..core.config import settings

LOG_LEVEL = str(LogLevel.DEBUG) if settings.DEBUG else str(settings.LOG_LEVEL)

LOGGING_CONFIG: dict[str, Any] = {
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
    logging.config.dictConfig(LOGGING_CONFIG)
