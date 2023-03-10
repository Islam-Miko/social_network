from collections.abc import Iterable, Mapping, Sequence
from typing import Any, ClassVar, TypeVar, Union

from fastapi import Depends
from sqlalchemy import delete, update
from sqlalchemy.ext.asyncio import AsyncResult, AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import exists as origin_exists

from app.dependencies import get_session

Model = TypeVar("Model")
Key = TypeVar("Key", str, int)


class BaseSqlAlchemyRepository:
    """
    Class for working with db
    """

    session: AsyncSession
    model: ClassVar

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        self.session = session

    async def create(self, instance: Model) -> Model:
        self.session.add(instance)
        await self.session.flush()
        await self.session.commit()
        return instance

    async def get(self, id: Key) -> Model:
        try:
            query = select(self.model).where(id == id)
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
            return result.first()
        except NoResultFound:
            raise

    async def all(
        self, limit: int, offset: int, *args: Sequence
    ) -> list[Model]:
        query = select(self.model).filter(self.model.deleted_at.is_(None))  # type: ignore
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
        query = select(self.model).filter(*args)
        result: AsyncResult = await self.session.execute(query)
        return result.scalars().first()

    async def delete(self, id: Key) -> None:
        query = delete(self.model).where(self.model.id == id)
        await self.session.execute(query)
        await self.session.commit()
