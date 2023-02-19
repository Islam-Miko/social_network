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

from app.configs.database import SessionFactory
from app.configs.environment import get_environment
from app.models.user_model import User
from app.repositories.user_repository import UserRepository

log = logging.getLogger(__name__)


class JWTAuthentication(AuthenticationBackend):
    settings = get_environment()

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
                self.settings.SECRET_KEY,
                algorithms=self.settings.HASH_ALGORITHM,
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

        session = SessionFactory()
        repo = UserRepository(session)

        try:
            user: User = await repo.get_by_login(login=login)
        except Exception:
            await session.close()
            raise AuthenticationError("Unable to authenticated!")
        else:
            await session.close()
            return AuthCredentials(["authenticated"]), user
