from datetime import date

from sqlalchemy.orm import Session

from ...authentication.models import User
from ..repositories import SqlAlchemyRepository


async def test_repository_can_create(session: Session):
    repo = SqlAlchemyRepository(session, User)
    instance = await repo.create(
        **{
            "first_name": "testname1",
            "last_name": "testlast",
            "birth_date": date(2999, 12, 31),
        }
    )
    await session.commit()
    assert isinstance(instance, User)
    assert await repo.exists(User.first_name == "testname1")


async def test_repository_can_retrive(session: Session):
    repo = SqlAlchemyRepository(session, User)
    instance = await repo.create(
        **{
            "first_name": "testname1",
            "last_name": "testlast",
            "birth_date": date(2999, 12, 31),
        }
    )
    await session.commit()

    user: User = await repo.get(User.id == instance.id)

    assert user.first_name == instance.first_name
    assert user.last_name == instance.last_name
    assert user.birth_date == instance.birth_date


async def test_repository_can_delete(session: Session):
    repo = SqlAlchemyRepository(session, User)
    instance: User = await repo.create(
        **{
            "first_name": "testname1",
            "last_name": "testlast",
            "birth_date": date(2999, 12, 31),
        }
    )

    await repo.delete(instance.id)

    await session.commit()
    assert await repo.exists(
        User.id == instance.id, User.deleted_at.is_not(None)
    )


async def test_repository_can_force_delete(session: Session):
    repo = SqlAlchemyRepository(session, User)
    instance: User = await repo.create(
        **{
            "first_name": "testname1",
            "last_name": "testlast",
            "birth_date": date(2999, 12, 31),
        }
    )

    await repo.force_delete(User.id == instance.id)

    await session.commit()
    exists = await repo.exists(
        User.id == instance.id, User.deleted_at.is_not(None)
    )
    assert not exists


async def test_repository_can_update(session: Session):
    repo = SqlAlchemyRepository(session, User)
    instance: User = await repo.create(
        **{
            "first_name": "testname1",
            "last_name": "testlast",
            "birth_date": date(2999, 12, 31),
        }
    )

    updated = await repo.update(instance.id, **dict(first_name="updated-1"))  # type: ignore

    await session.commit()
    assert updated.first_name != "testname1"
    assert updated.last_name == "testlast"
    assert updated.birth_date == date(2999, 12, 31)


async def test_repository_get_or_none(session: Session):
    repo = SqlAlchemyRepository(session, User)
    none_result = await repo.get_or_none(User.first_name == "empty")
    assert none_result is None

    instance: User = await repo.create(
        **{
            "first_name": "testname1",
            "last_name": "testlast",
            "birth_date": date(2999, 12, 31),
        }
    )
    await session.commit()

    result = await repo.get_or_none(User.id == instance.id)
    assert result is not None
