from datetime import datetime

from ormar import pre_update

from .account import Account


@pre_update([Account])
async def before_update(sender, instance, **kwargs):
    """
    A callback function that automatically updates
    the 'updated_at' field with the current time.
    """
    setattr(instance, "updated_at", datetime.now())
