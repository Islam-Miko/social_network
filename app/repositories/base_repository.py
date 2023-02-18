from collections.abc import Iterable, Mapping, Sequence
from datetime import datetime
from typing import Any, ClassVar, TypeVar

from fastapi import Depends
from sqlalchemy import update
from sqlalchemy.engine import Result, ResultProxy
from sqlalchemy.ext.asyncio import AsyncSession
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

    __session: AsyncSession
    model: ClassVar

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        self.__session = session

    async def create(self, instance: Model) -> Model:
        self.__session.add(instance)
        await self.__session.flush()
        return instance

    async def get(self, id: Key) -> Model:
        try:
            query = select(self.model).where(id == id)
            result: ResultProxy = await self.__session.execute(query)
            return result.scalars().one()
        except NoResultFound:
            raise  # TODO handle

    async def delete(self, id: Key) -> None:
        try:
            query = (
                update(self.model)
                .where(self.model.id == id)  # type: ignore
                .values(deleted_at=datetime.now())
            )
            result: ResultProxy = await self.__session.execute(query)
            return result.one_or_none()
        except NoResultFound:
            raise

    async def update(self, id: Key, data: Mapping[str, Any]) -> Model:
        try:
            query = (
                update(self.model)
                .filter(self.model.id == id)  # type: ignore
                .returning(self.model)
                .values(**data)
            )
            result: ResultProxy = await self.__session.execute(query)
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
        result: ResultProxy = await self.__session.execute(query)
        return result.scalars().all()

    async def exists(self, *args: Iterable) -> bool:
        query = origin_exists(self.model).where(*args).select()
        result: Result = await self.__session.execute(query)
        return result.scalar_one()
