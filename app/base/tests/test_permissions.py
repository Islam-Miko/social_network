from typing import Optional, Union

import pytest
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.testclient import TestClient
from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    AuthenticationError,
)
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.requests import HTTPConnection

from ..permissions import permission_classes


class FakeAuthentication(AuthenticationBackend):
    def init(
        self,
        exception: Optional[HTTPException] = None,
    ):
        if exception is not None:
            exception = self.default_exception
        self.exception = exception

    async def authenticate(
        self, conn: HTTPConnection
    ) -> Optional[tuple["AuthCredentials", Union[None, int]]]:
        auth = conn.headers.get("Authorization")
        if auth is None:
            return AuthCredentials(["authenticated"]), None
        scheme, credentials = auth.split()
        if scheme.lower() != "test":
            raise AuthenticationError("WRONG_TOKEN_TYPE_TEST")
        return AuthCredentials(["authenticated"]), int(credentials)


class GreatedThan100:
    @classmethod
    async def has_permission(cls, request: Request) -> bool:
        if request.user is None:
            return False
        return request.user > 100


@pytest.fixture
def app_permissioned():
    app = FastAPI()
    app.add_middleware(AuthenticationMiddleware, backend=FakeAuthentication())

    @app.get("/{mega}/")
    @permission_classes([GreatedThan100])
    async def ping(request: Request, mega: str, Authorization=Header(...)):
        return 202

    return app


async def test_permission_handler_auth(app_permissioned):
    client = TestClient(app_permissioned)

    response = client.get("/ultra/", headers={"Authorization": "test 500"})
    assert response.status_code == 200
    assert response.text == "202"


async def test_permission_handler_noauth(app_permissioned):
    client = TestClient(app_permissioned)

    response = client.get("/ultra/", headers={"Authorization": "test 99"})
    assert response.status_code == 403
