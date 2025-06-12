"""Source package for the FastAPI TDD application.

This package contains all the core logic, models, services, controllers,
and utilities for the application. It re-exports key models or components
as needed.

Exports:
    Account: The main user account model from `src.models.account`.
"""
from .models.account import Account

__all__ = ["Account"]
