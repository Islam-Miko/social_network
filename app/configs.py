from pydantic import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    hash_algorithm: str
    access_token_lifetime: int
    refresh_token_lifetime: int

    class Config:
        env_file = BASE_DIR / ".env"