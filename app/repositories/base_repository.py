from collections.abc import Iterable, Mapping, Sequence
from typing import Any, ClassVar, TypeVar, Union

from fastapi import Depends
from sqlalchemy import Select, delete, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncResult, AsyncSession
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import exists as origin_exists

from app.configs.database import get_session

Model = TypeVar("Model")
Key = TypeVar("Key", str, int)


class BaseSqlAlchemyRepository:
    """
    Class for working with db
    """

    session: AsyncSession
    model: ClassVar
    base_select: Select

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        self.session = session

    async def create(self, data: Mapping) -> Model:
        query = insert(self.model).values(**data).returning(self.model.id)
        result: AsyncResult = await self.session.execute(query)
        await self.session.commit()
        return result.scalar_one()

    async def get(self, id: Key) -> Model:
        try:
            query = self.base_select.where(self.model.id == id)
            result: AsyncResult = await self.session.execute(query)
            return result.scalars().one()
        except NoResultFound:
            raise  # TODO handle

    async def update(self, id: Key, data: Mapping[str, Any]) -> Model:
        try:
            query = (
                update(self.model)
                .filter(self.model.id == id)  # type: ignore
                .returning(self.model)
                .values(**data)
            )
            result: AsyncResult = await self.session.execute(query)
            await self.session.commit()
            return result.scalar_one()
        except NoResultFound:
            raise

    async def all(
        self, limit: int, offset: int, *args: Sequence
    ) -> list[Model]:
        query = self.base_select  # type: ignore
        if args:
            query.filter(*args)
        query = query.limit(limit).offset(offset)
        result: AsyncResult = await self.session.execute(query)
        return result.scalars().all()

    async def exists(self, *args: Iterable) -> bool:
        query = origin_exists(self.model).where(*args).select()
        result: AsyncResult = await self.session.execute(query)
        return result.scalar_one()

    async def get_or_none(self, *args: Iterable) -> Union[None, Model]:
        query = self.base_select.where(*args)
        result: AsyncResult = await self.session.execute(query)
        return result.scalars().first()

    async def delete(self, id: Key) -> None:
        query = delete(self.model).where(self.model.id == id)
        await self.session.execute(query)
        await self.session.commit()

    async def count(self, *args) -> int:
        query = (
            select(func.count())
            .select_from(self.model)
            .where(self.model.deleted_at.is_(None))
            .where(*args)
        )
        result: AsyncResult = await self.session.execute(query)
        return result.scalar_one()
