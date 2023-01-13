from datetime import datetime

from fastapi import HTTPException, Request
from sqlalchemy import update
from sqlalchemy.engine import Result
from sqlalchemy.sql import exists as origin_exists

from app import messages

from ..base.repositories import SqlAlchemyRepository
from .models import Like, Post


async def delete_self_post(id: int, repo: SqlAlchemyRepository) -> None:
    query = (
        update(repo.model)
        .filter(repo.model.id == id)
        .returning(repo.model)
        .values(deleted_at=datetime.utcnow())
    )
    await repo.execute_query(query)


async def check_if_post_owner(
    id: int, user_id: int, repo: SqlAlchemyRepository
) -> bool:
    query = (
        origin_exists(Post)
        .where(Post.id == id, Post.owner == user_id)
        .select()
    )
    result: Result = await repo.execute_query(query, return_result=True)
    return result


async def check_and_delete_post(id: int, request: Request) -> None:
    session = request.state.dbsession()
    repo = SqlAlchemyRepository(session, Post)

    is_owner = await check_if_post_owner(id, request.user.id, repo)
    if not is_owner:
        raise HTTPException(
            status_code=400,
            detail=messages.ACTION_NOT_ALLOWED,
        )
    await delete_self_post(id, repo)
    await session.commit()
    await session.close()


async def check_for_self_post(
    post_id: int, user_id: int, repo: SqlAlchemyRepository
) -> None:
    is_owner = await check_if_post_owner(post_id, user_id, repo)
    if is_owner:
        raise HTTPException(
            status_code=400,
            detail=messages.ACTION_NOT_ALLOWED,
        )


async def like_post(post_id: int, request: Request) -> None:
    session = request.state.dbsession()
    repo = SqlAlchemyRepository(session, Post)

    await check_for_self_post(post_id, request.user.id, repo)
    statement = Like.insert().values(user_id=request.user.id, post_id=post_id)
    await repo.execute_query(statement)
    await session.commit()
    await session.close()


async def dislike_post(post_id: int, request: Request) -> None:
    session = request.state.dbsession()
    repo = SqlAlchemyRepository(session, Post)
    user_id = request.user.id

    await check_for_self_post(post_id, user_id, repo)
    statement = Like.delete().where(
        Like.c.user_id == user_id, Like.c.post_id == post_id
    )
    await repo.execute_query(statement)
    await session.commit()
    await session.close()
