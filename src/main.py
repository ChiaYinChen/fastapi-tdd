from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .controllers import account
from .core.config import settings
from .db.session import base_ormar_config


def get_lifespan(config):
    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        if not config.database.is_connected:
            await config.database.connect()

        yield

        if config.database.is_connected:
            await config.database.disconnect()

    return lifespan


app = FastAPI(lifespan=get_lifespan(base_ormar_config))
app.include_router(account.router, prefix=f"{settings.API_PREFIX}/accounts", tags=["accounts"])
