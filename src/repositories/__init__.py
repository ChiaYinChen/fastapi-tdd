"""Repositories package for data access logic.

This package provides repository classes that encapsulate the logic for
accessing and manipulating data from various sources, typically databases.
It promotes a separation of concerns by isolating data access operations.

Exports:
    account (AccountRepository): Repository for account data operations.
"""
from .account import account  # noqa: F401
