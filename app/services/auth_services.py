from datetime import datetime, timedelta
from typing import Any, Dict

from fastapi import Depends, HTTPException, status
from jose import jwt
from passlib.context import CryptContext
from starlette.authentication import AuthenticationError

from app import messages
from app.configs.environment import get_environment
from app.exceptions import InvalidTokenError
from app.models.user_model import Credential, RefreshToken
from app.schemas.auth_schema import (
    AuthenticationSchema,
    CredentialSchema,
    RefreshTokenSchema,
    RegistrationSchema,
    TokensSchema,
)
from app.services.user_service import (
    CredentialService,
    RefreshTokenService,
    UserService,
)


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

    settings = get_environment()

    async def authorize(
        self, login: str, password: str, service: CredentialService
    ) -> Credential:
        """
        Authenticate user
        """
        user_credential = await service.get_or_none(Credential.login == login)  # type: ignore

        if user_credential is None:
            raise AuthenticationError("Invalid credentials.")

        if not self.handler.verify_password(
            password, user_credential.password
        ):
            raise AuthenticationError("Invalid credentials.")
        return user_credential

    async def generate_token(
        self, token_type: str = "access", data: Dict[str, Any] = dict()
    ) -> tuple[str, float]:
        """
        Generate jwt token
        """
        token_lifetime = {
            "access": self.settings.ACCESS_TOKEN_LIFETIME,
            "refresh": self.settings.REFRESH_TOKEN_LIFETIME,
        }
        expires_delta = timedelta(minutes=token_lifetime.get(token_type))
        expires_at = datetime.timestamp(datetime.utcnow() + expires_delta)
        data.update({"expiration_date": expires_at})
        encoded = jwt.encode(
            data, self.settings.SECRET_KEY, self.settings.HASH_ALGORITHM
        )
        return encoded, expires_at

    async def refresh_token(
        self,
        access_token: str,
        refresh_token: str,
        service: RefreshTokenService,
    ) -> tuple[str, float]:
        """
        Generate new access token by given refresh token
        """
        payload = jwt.decode(
            access_token,
            self.settings.SECRET_KEY,
            options={"verify_exp": False},
        )
        _, key, _ = refresh_token.split(".")
        instance = await service.get_or_none(RefreshToken.key == key)
        if datetime.utcnow() > datetime.fromtimestamp(instance.valid_until):
            raise InvalidTokenError(messages.EXPIRED_TOKEN)

        expires_at = datetime.timestamp(
            datetime.utcnow()
            + timedelta(minutes=self.settings.ACCESS_TOKEN_LIFETIME)
        )
        payload.update(exp=expires_at)
        encoded = jwt.encode(
            payload,
            self.settings.SECRET_KEY,
            self.settings.HASH_ALGORITHM,
        )
        return encoded, expires_at


class AuthService:
    handler: AuthenticationHandler

    def __init__(self, handler: AuthenticationHandler = Depends()) -> None:
        self.handler = handler

    async def access_token(
        self,
        data: AuthenticationSchema,
        credential_service: CredentialService,
        refresh_service: RefreshTokenService,
    ) -> TokensSchema:
        user_credential = await self.handler.authorize(
            **data.dict(), service=credential_service
        )
        access_token, _ = await self.handler.generate_token(
            data={"user": user_credential.login}
        )
        refresh_token, exp_at = await self.handler.generate_token(
            token_type="refresh", data={"user": user_credential.id}
        )
        _, key, _ = refresh_token.split(".")

        refresh = await refresh_service.get_or_none(  # type: ignore
            RefreshToken.owner == user_credential.id
        )
        if refresh is not None:
            await refresh_service.delete(refresh.id)  # type: ignore
        await refresh_service.create(
            RefreshTokenSchema(
                key=key, owner=user_credential.user_id, valid_until=exp_at
            )
        )  # type: ignore
        return TokensSchema(
            access_token=access_token, refresh_token=refresh_token
        )

    async def register(
        self,
        data: RegistrationSchema,
        user_service: UserService,
        credential_service: CredentialService,
    ) -> None:
        try:
            await user_service.get_by_login(data.login)
        except Exception:
            pass
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=messages.ALREADY_REGISTERED,
            )

        password_hash = self.handler.handler.get_hash(data.password)
        user_id = await user_service.create(data)
        await credential_service.create(
            CredentialSchema(
                login=data.login, password=password_hash, user_id=user_id
            )
        )  # type: ignore

    async def generate_new(
        self, data: TokensSchema, service: RefreshTokenService
    ) -> TokensSchema:
        access_token, _ = await self.handler.refresh_token(
            **data.dict(), service=service
        )
        return TokensSchema(access_token=access_token, refresh_token="")
