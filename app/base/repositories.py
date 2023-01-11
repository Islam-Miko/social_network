import abc
from datetime import datetime
from typing import Any, Iterable, Mapping, Union

from sqlalchemy import delete, update
from sqlalchemy.engine import Result, ResultProxy
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import exists as origin_exists

from .models import BaseModel


class ABCRepository(abc.ABC):
    @abc.abstractmethod
    async def create(self, **data: Mapping) -> Any:
        raise NotImplementedError

    @abc.abstractmethod
    async def get(self, *args: Iterable, **kwargs: Mapping) -> Any:
        raise NotImplementedError

    @abc.abstractmethod
    async def delete(self, pk: int) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def update(self, pk: int, *args: Iterable, **kwargs: Mapping) -> Any:
        raise NotImplementedError


class SqlAlchemyRepository(ABCRepository):
    def __init__(self, session: Session, model: BaseModel) -> None:
        self.__session = session
        self.model = model

    async def create(self, **data: Mapping) -> Any:
        instance = self.model(**data)
        self.__session.add(instance)
        await self.__session.flush()
        return instance

    async def get(self, *args: Iterable, **kwargs: Mapping) -> Any:
        try:
            query = select(self.model).filter(*args, **kwargs)
            result: ResultProxy = await self.__session.execute(query)
            return result.scalars().one()
        except NoResultFound:
            raise  # TODO handle

    async def delete(self, pk: int) -> None:
        try:
            query = (
                update(self.model)
                .filter(self.model.id == pk)
                .values(deleted_at=datetime.utcnow())
            )
            result: ResultProxy = await self.__session.execute(query)
            return result.one_or_none()
        except NoResultFound:
            raise

    async def update(self, pk: int, *args: Iterable, **kwargs: Mapping) -> Any:
        try:
            query = (
                update(self.model)
                .filter(self.model.id == pk)
                .returning(self.model)
                .values(**kwargs)
            )
            result: ResultProxy = await self.__session.execute(query)
            return result.first()
        except NoResultFound:
            raise

    async def all(self, *args: Iterable, **kwargs: Mapping) -> list:
        query = select(self.model).filter(self.model.deleted_at.is_(None))
        if args:
            query.filter(*args)
        result: ResultProxy = await self.__session.execute(query)
        return result.scalars().all()

    async def get_or_none(self, *args: Iterable) -> Union[None, Any]:
        query = select(self.model).filter(*args)
        result: Result = await self.__session.execute(query)
        return result.scalars().first()

    async def exists(self, *args: Iterable) -> bool:
        query = origin_exists(self.model).where(*args).select()
        result: Result = await self.__session.execute(query)
        return result.scalar_one()

    async def force_delete(self, *args: Iterable) -> None:
        query = delete(self.model).filter(*args)
        await self.__session.execute(query)
