from functools import lru_cache
from pathlib import Path

from pydantic import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    DATABASE_HOST: str
    DATABASE_DB: str
    DATABASE_PORT: int
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    ASYNC_DRIVER: str = "postgresql+asyncpg"
    SYNC_DRIVER: str = "postgresql"
    SECRET_KEY: str
    HASH_ALGORITHM: str
    ACCESS_TOKEN_LIFETIME: int
    REFRESH_TOKEN_LIFETIME: int

    class Config:
        env_file = BASE_DIR / ".env"


@lru_cache
def get_environment() -> Settings:
    return Settings()
