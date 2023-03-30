from collections.abc import Sequence
from datetime import date
from typing import Optional, Union

from fastapi import Depends

from app.models.user_model import Credential, RefreshToken, User
from app.repositories.user_repository import (
    CredentialRepository,
    RefreshTokenRepository,
    UserRepository,
)
from app.schemas.auth_schema import (
    CredentialSchema,
    RefreshTokenSchema,
    RegistrationSchema,
)


class UserService:
    repository: UserRepository

    def __init__(self, repository: UserRepository = Depends()) -> None:
        self.repository = repository

    async def search_user(
        self,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        substr: Optional[str] = None,
        birth_date: Optional[date] = None,
    ) -> list[User]:
        return await self.repository.search(
            first_name=first_name,
            last_name=last_name,
            substr=substr,
            birth_date=birth_date,
        )

    async def create(self, data: RegistrationSchema) -> int:
        return await self.repository.create(
            data.dict(exclude={"login", "password"})
        )

    async def get_by_login(self, login: str) -> User:
        return await self.repository.get_by_login(login)


class CredentialService:
    repository: CredentialRepository

    def __init__(self, repository: CredentialRepository = Depends()) -> None:
        self.repository = repository

    async def get_or_none(self, *args: Sequence) -> Union[None, Credential]:
        return await self.repository.get_or_none(*args)

    async def create(self, data: CredentialSchema) -> Credential:
        return await self.repository.create(data.dict())


class RefreshTokenService:
    repository: RefreshTokenRepository

    def __init__(self, repository: RefreshTokenRepository = Depends()) -> None:
        self.repository = repository

    async def get_or_none(self, *args: Sequence) -> Union[None, RefreshToken]:
        return await self.repository.get_or_none(*args)

    async def delete(self, id: int) -> None:
        await self.repository.delete(id)

    async def create(
        self, data: RefreshTokenSchema
    ) -> Union[None, RefreshToken]:
        return await self.repository.create(data.dict())
