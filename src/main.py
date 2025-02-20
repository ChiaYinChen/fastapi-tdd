from fastapi import FastAPI

from .controllers import account
from .core.config import settings

app = FastAPI()
app.include_router(account.router, prefix=f"{settings.API_PREFIX}/accounts", tags=["accounts"])
