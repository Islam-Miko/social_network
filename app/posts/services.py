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


async def check_for_self_post(
    id: int, user_id: int, repo: SqlAlchemyRepository
) -> None:
    query = (
        origin_exists(Post)
        .where(Post.id == id, Post.owner == user_id)
        .select()
    )
    result: Result = await repo.execute_query(query, return_result=True)
    if not result:
        raise HTTPException(
            status_code=400,
            detail=messages.ACTIONS_NOT_ALLOWED_ON_SELF_OBJECTS,
        )


async def check_and_delete_post(id: int, request: Request) -> None:
    session = request.state.dbsession()
    repo = SqlAlchemyRepository(session, Post)

    await check_for_self_post(id, request.user.id, repo)
    await delete_self_post(id, repo)
    await session.commit()
    await session.close()


async def like_post(post_id: int, request: Request) -> None:
    session = request.state.dbsession()
    repo = SqlAlchemyRepository(session, Post)

    await check_for_self_post(post_id, request.user.id, repo)
    post: Post = await repo.get(Post.id == post_id)
    statement = Like.insert().values(user_id=request.user.id, post_id=post.id)
    await repo.execute_query(statement)
    await session.commit()
    await session.close()
