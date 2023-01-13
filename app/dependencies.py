from functools import lru_cache
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from .configs import Settings
from .db import async_session


@lru_cache
def get_settings() -> Settings:
    return Settings()


async def get_db() -> AsyncIterator[AsyncSession]:
    async with async_session() as session:
        yield session
