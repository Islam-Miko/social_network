from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.configs.environment import Settings, get_environment

ENV = get_environment()


def get_database_url(env: Settings) -> str:
    database_url = (
        f"{env.ASYNC_DRIVER}://{env.DATABASE_USER}:{env.DATABASE_PASSWORD}"
        f"@{env.DATABASE_HOST}:{env.DATABASE_PORT}/{env.DATABASE_DB}"
    )
    return database_url


database_url = get_database_url(ENV)

db_engine = create_async_engine(database_url, future=True, echo=True)

SessionFactory = sessionmaker(
    db_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)
