from datetime import datetime, timedelta
from functools import lru_cache
from typing import Any, Dict

from jose import jwt
from passlib.context import CryptContext
from starlette.authentication import AuthenticationError

from app import messages

from ..base.repositories import SqlAlchemyRepository
from ..db import async_session
from ..dependencies import get_settings
from ..exceptions import InvalidTokenError
from .models import Credential, RefreshToken


class PasswordHandler:
    context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def verify_password(cls, plain_pass: str, hash_pass: str) -> bool:
        return cls.context.verify(plain_pass, hash_pass)

    @classmethod
    def get_hash(cls, password: str) -> str:
        return cls.context.hash(password)


class AuthenticationHandler:
    handler = PasswordHandler
    settings = get_settings()

    async def authorize(self, login: str, password: str):
        session = async_session()
        repo = SqlAlchemyRepository(session, Credential)
        user_credential = await repo.get_or_none(Credential.login == login)  # type: ignore

        if user_credential is None:
            raise AuthenticationError("Invalid credentials.")

        if not self.handler.verify_password(
            password, user_credential.password
        ):
            raise AuthenticationError("Invalid credentials.")
        await session.close()
        return user_credential

    async def generate_token(
        self, token_type: str = "access", data: Dict[str, Any] = dict()
    ):
        token_lifetime = {
            "access": self.settings.access_token_lifetime,
            "refresh": self.settings.refresh_token_lifetime,
        }
        expires_delta = timedelta(minutes=token_lifetime.get(token_type))
        expires_at = datetime.timestamp(datetime.utcnow() + expires_delta)
        data.update({"expiration_date": expires_at})
        encoded = jwt.encode(
            data, self.settings.secret_key, self.settings.hash_algorithm
        )
        return encoded, expires_at

    async def refresh_token(
        self, access_token: str, refresh_token: str
    ) -> tuple[str, float]:
        session = async_session()
        repo = SqlAlchemyRepository(session, RefreshToken)
        payload = jwt.decode(
            access_token,
            self.settings.secret_key,
            options={"verify_exp": False},
        )
        _, key, _ = refresh_token.split(".")
        instance = await repo.get(RefreshToken.key == key)
        await session.close()
        if datetime.now() > datetime.fromtimestamp(instance.valid_until):
            raise InvalidTokenError(messages.EXPIRED_TOKEN)

        expires_at = datetime.timestamp(
            datetime.utcnow()
            + timedelta(minutes=self.settings.access_token_lifetime)
        )
        payload.update(exp=expires_at)
        encoded = jwt.encode(
            payload,
            self.settings.secret_key,
            self.settings.hash_algorithm,
        )
        return encoded, expires_at


@lru_cache
def get_authentication_handler() -> AuthenticationHandler:
    return AuthenticationHandler()
