"""Defines logging level constants for the application.

This module provides an enumeration for standard logging levels.
"""
from enum import Enum


class LogLevel(str, Enum):
    """Enumeration of logging levels.

    These levels correspond to standard logging levels and can be used
    to configure the application's logger.

    Attributes:
        DEBUG (str): Detailed information, typically of interest only when diagnosing problems.
        INFO (str): Confirmation that things are working as expected.
        WARNING (str): An indication that something unexpected happened, or indicative of some problem in the near future.
        ERROR (str): Due to a more serious problem, the software has not been able to perform some function.
        CRITICAL (str): A serious error, indicating that the program itself may be unable to continue running.
    """
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

    def __str__(self) -> str:
        """Return the string representation of the log level.

        Returns:
            str: The string value of the log level enum member.
        """
        return str(self.value)
