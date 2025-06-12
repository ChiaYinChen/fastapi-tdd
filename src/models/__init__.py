"""Models package for the application.

This package defines the data models (e.g., Ormar models) used by the application.
It also includes any model-related utility functions or lifecycle hooks,
such as the `before_update` hook to automatically update `updated_at` timestamps.
"""
from datetime import datetime

from ormar import pre_update

from .account import Account


@pre_update([Account])
async def before_update(sender: type, instance: Account, **kwargs) -> None:
    """Automatically updates the 'updated_at' field before an instance is saved.

    This function is registered as a pre-update hook for models like `Account`.
    It sets the `updated_at` attribute of the instance to the current UTC datetime.

    Args:
        sender (type): The model class that sent the signal.
        instance (Account): The instance being saved.
        **kwargs: Additional keyword arguments passed by the signal.
    """
    setattr(instance, "updated_at", datetime.now(datetime.UTC))
