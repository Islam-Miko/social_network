import asyncio
import logging
import os
import tempfile

import alembic
import httpx
import psycopg2
import pytest
import pytest_asyncio
import yaml
from alembic.config import Config
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def event_loop():
    """
    Create event loop instance for testing
    """
    loop = asyncio.get_event_loop_policy().get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def postgres_data(docker_ip):
    return {
        "postgres": {
            "dbname": "webtronics-test",
            "user": "postgres",
            "password": "postgres",
            "host": docker_ip,
        }
    }


@pytest.fixture(scope="session")
def get_database_url(postgres_data):
    return "postgresql+asyncpg://{}:{}@{}/{}".format(
        postgres_data["postgres"]["user"],
        postgres_data["postgres"]["password"],
        postgres_data["postgres"]["host"],
        postgres_data["postgres"]["dbname"],
    )


@pytest.fixture(scope="session")
def docker_tmpfile():
    tf = tempfile.mkstemp()
    yield tf
    os.remove(tf[1])


@pytest.fixture(scope="session")
def docker_compose_file(docker_tmpfile, postgres_data):
    content = {
        "version": "3.7",
        "services": {
            "postgresql": {
                "image": "postgres:13-alpine",
                "ports": ["5432:5432"],
                "environment": [
                    "POSTGRES_PASSWORD={}".format(
                        postgres_data["postgres"]["password"]
                    ),
                    "POSTGRES_USER={}".format(
                        postgres_data["postgres"]["user"]
                    ),
                    "POSTGRES_DB={}".format(
                        postgres_data["postgres"]["dbname"]
                    ),
                ],
            }
        },
    }
    f = os.fdopen(docker_tmpfile[0], "w")
    f.write(yaml.dump(content))
    f.close()
    return docker_tmpfile[1]


def is_responsive(ip, postgres_data):
    try:
        conn = psycopg2.connect(
            host=ip,
            user=postgres_data["postgres"]["user"],
            password=postgres_data["postgres"]["password"],
            dbname=postgres_data["postgres"]["dbname"],
        )
        conn.close()
    except Exception:
        return False
    else:
        return True


@pytest_asyncio.fixture(scope="session")
async def db_engine(
    docker_ip, docker_services, postgres_data, get_database_url
):
    docker_services.wait_until_responsive(
        timeout=15,
        pause=2,
        check=lambda: is_responsive(docker_ip, postgres_data),
    )
    default_engine = create_async_engine(get_database_url)

    yield default_engine


@pytest.fixture
def apply_migrations(get_database_url):
    os.environ["DATABASE_URL"] = get_database_url
    config = Config("alembic.ini")
    alembic.command.upgrade(config, "head")
    yield


@pytest_asyncio.fixture
async def session(db_engine, apply_migrations):
    session = sessionmaker(
        db_engine, expire_on_commit=False, class_=AsyncSession
    )()
    yield session
    await session.close()


@pytest_asyncio.fixture
async def client():
    from app.server import get_application

    app = get_application()
    async with httpx.AsyncClient(app=app, base_url="http://testing") as client:
        yield client
