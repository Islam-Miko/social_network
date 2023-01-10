from typing import Callable
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from .dependencies import get_settings


def create_engine() -> Callable[..., Session]:
    settings = get_settings()
    
    database_url = settings.database_url

    psql_engine = create_async_engine(
        database_url, future=True, echo=settings.echo
    )

    return sessionmaker(
        psql_engine, expire_on_commit=False, class_=AsyncSession
    )

async_session = create_engine()