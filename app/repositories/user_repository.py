from datetime import date
from typing import Optional

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncResult

from app.models.user_model import Credential, RefreshToken, User
from app.repositories.base_repository import BaseSqlAlchemyRepository


class UserRepository(BaseSqlAlchemyRepository):
    model = User

    async def search(
        self,
        first_name: Optional[str],
        last_name: Optional[str],
        substr: Optional[str],
        birth_date: Optional[date],
    ) -> list[User]:
        query = select(self.model).where(self.model.deleted_at.is_(None))

        if first_name:
            query = query.where(self.model.first_name == first_name)

        if last_name:
            query = query.where(self.model.last_name == last_name)

        if substr:
            query = query.where(
                or_(
                    User.last_name.icontains(substr),
                    User.first_name.icontains(substr),
                )
            )

        if birth_date:
            query = query.where(self.model.birth_date == birth_date)
        result: AsyncResult = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_login(self, login: str) -> User:
        query = select(self.model).where(
            self.model.deleted_at.is_(None),
            self.model.credentials.has(Credential.login == login),
        )
        result: AsyncResult = await self.session.execute(query)
        return result.scalars().one()


class CredentialRepository(BaseSqlAlchemyRepository):
    model = Credential


class RefreshTokenRepository(BaseSqlAlchemyRepository):
    model = RefreshToken
