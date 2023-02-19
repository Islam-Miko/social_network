# type: ignore
from httpx import AsyncClient
from sqlalchemy.orm import Session

from ...base.repositories import SqlAlchemyRepository
from ..models import Credential, User


async def test_registration(client: AsyncClient, session: Session):
    data = {
        "first_name": "fake_name",
        "last_name": "fake_lname",
        "birth_date": "2000-10-10",
        "password": "today",
        "login": "FakeJD",
    }
    response = await client.post("/auth/register/", json=data)

    assert response.status_code == 201
    body = response.json()
    assert "message" in body

    credential_repo = SqlAlchemyRepository(session, Credential)
    user_repo = SqlAlchemyRepository(session, User)

    assert await credential_repo.exists(Credential.login == data["login"])
    assert await user_repo.exists(
        User.credentials.any(Credential.login == data["login"])
    )


async def test_access_token(client: AsyncClient):
    data = {
        "first_name": "fn",
        "last_name": "ln",
        "birth_date": "2000-10-10",
        "password": "today",
        "login": "JD",
    }
    response = await client.post("/auth/register/", json=data)

    assert response.status_code == 201

    data = {"login": "JD", "password": "today"}
    response = await client.post("/auth/access-token/", json=data)
    assert response.status_code == 200

    response_body = response.json()

    assert "access_token" in response_body
    assert "refresh_token" in response_body


async def test_refresh_token(client: AsyncClient):
    data = {
        "first_name": "refresh",
        "last_name": "ln",
        "birth_date": "2000-10-10",
        "password": "today",
        "login": "RefreshJD",
    }
    response = await client.post("/auth/register/", json=data)

    assert response.status_code == 201

    data = {"login": "RefreshJD", "password": "today"}
    response = await client.post("/auth/access-token/", json=data)
    assert response.status_code == 200

    response_body = response.json()

    assert "access_token" in response_body
    assert "refresh_token" in response_body

    refreshed_response = await client.post(
        "/auth/refresh-token/", json=response_body
    )
    assert refreshed_response.status_code == 200

    body = refreshed_response.json()
    assert body["access_token"] != response_body["access_token"]
