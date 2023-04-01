from datetime import date
from typing import Union

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncResult, AsyncSession

from app.models.user_model import User
from app.repositories.user_repository import UserRepository


@pytest_asyncio.fixture(scope="session")
async def user_instance(session: AsyncSession) -> User:
    repo = UserRepository(session)
    instance: User = await repo.create(
        {
            "first_name": "testname1",
            "last_name": "testlast",
            "birth_date": date(2999, 12, 31),
        }
    )
    await session.commit()
    return instance


async def test_repository_can_create(
    session: AsyncSession, user_instance: User
):
    repo = UserRepository(session)
    await session.commit()
    assert isinstance(user_instance, User)
    assert await repo.exists(User.first_name == "testname1")


async def test_repository_can_retrive(
    session: AsyncSession, user_instance: User
):
    repo = UserRepository(session)

    user: User = await repo.get(User.id == user_instance.id)

    assert user.first_name == user_instance.first_name
    assert user.last_name == user_instance.last_name
    assert user.birth_date == user_instance.birth_date


async def test_repository_can_delete(
    session: AsyncSession, user_instance: User
):
    repo = UserRepository(session)
    assert await repo.exists(
        User.id == user_instance.id, User.deleted_at.is_not(None)
    )


async def test_repository_can_force_delete(
    session: AsyncSession, user_instance: User
):
    repo = UserRepository(session)

    await repo.delete(User.id == user_instance.id)
    await session.commit()
    exists = await repo.exists(
        User.id == user_instance.id, User.deleted_at.is_not(None)
    )
    assert not exists


async def test_repository_can_update(
    session: AsyncSession, user_instance: User
):
    repo = UserRepository(session)

    updated = await repo.update(user_instance.id, dict(first_name="updated-1"))  # type: ignore

    await session.commit()
    assert updated.first_name != "testname1"
    assert updated.last_name == "testlast"
    assert updated.birth_date == date(2999, 12, 31)


async def test_repository_get_or_none(
    session: AsyncSession, user_instance: User
):
    repo = UserRepository(session)
    none_result: AsyncResult = await repo.get_or_none(
        User.first_name == "empty"
    )
    assert none_result is None
    result: Union[User, None] = await repo.get_or_none(
        User.id == user_instance.id
    )
    assert result is not None
