import logging
import typing
from datetime import datetime

from jose import ExpiredSignatureError, JWTError, jwt
from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    AuthenticationError,
)
from starlette.requests import HTTPConnection

from ..base.repositories import SqlAlchemyRepository
from ..db import async_session
from ..dependencies import get_settings
from .models import User

log = logging.getLogger(__name__)


class JWTAuthentication(AuthenticationBackend):
    settings = get_settings()

    async def authenticate(
        self, conn: HTTPConnection
    ) -> typing.Optional[typing.Tuple["AuthCredentials", "User"]]:
        credentials = conn.headers.get("Authorization")
        if credentials is None:
            return AuthCredentials(["authenticated"]), None

        scheme, token = credentials.split()
        if scheme.lower() != "bearer":
            log.warning("ERROR: scheme is incorrect")
            raise AuthenticationError("Incorrect token type!")
        try:
            payload = jwt.decode(
                token,
                self.settings.secret_key,
                algorithms=self.settings.hash_algorithm,
            )
            login = payload.get("user")
            if login is None:
                log.warning("ERROR: something went wrong!")
                raise AuthenticationError("Wrong token!")

            if datetime.utcnow() > datetime.fromtimestamp(
                payload.get("expiration_date")
            ):
                raise ExpiredSignatureError("Signature expired!")
        except JWTError as e:
            log.warning(f"ERROR: {e}")
            raise AuthenticationError("Failed to decode JWT!") from e
        session = async_session()
        repo = SqlAlchemyRepository(session, User)
        user: User = await repo.get(User.credentials.login == login)
        return AuthCredentials(["authenticated"]), user
