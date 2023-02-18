from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from app.configs.database import SessionFactory


async def get_session() -> AsyncIterator[AsyncSession]:
    session = SessionFactory()
    try:
        yield session
    finally:
        await session.close()
