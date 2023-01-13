from fastapi import APIRouter, Depends, Header, Request
from fastapi_pagination import LimitOffsetPage
from fastapi_pagination.ext.async_sqlalchemy import paginate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..base.permissions import IsAuthenticated, permission_classes
from ..base.repositories import SqlAlchemyRepository
from ..dependencies import get_db
from .models import Post
from .schema import PostCreateSchema, UpdatePostSchema
from .services import check_and_delete_post
from .services import dislike_post as user_dislike_post
from .services import like_post as user_like_post

router = APIRouter(prefix="/posts")


@router.get("/", response_model=LimitOffsetPage)
@permission_classes(
    [
        IsAuthenticated,
    ]
)
async def get_posts(
    request: Request,
    session: AsyncSession = Depends(get_db),
    Authorization: str = Header(...),
):
    return await paginate(
        session,
        select(Post).filter(Post.deleted_at.is_(None)),
    )


@router.post("/", status_code=201)
@permission_classes(
    [
        IsAuthenticated,
    ]
)
async def create_post(
    request: Request, data: PostCreateSchema, Authorization: str = Header(...)
):
    session = request.state.dbsession()
    repo = SqlAlchemyRepository(session, Post)
    created = await repo.create(**data.dict(), owner=request.user.id)
    await session.commit()
    await session.close()
    return created


@router.get("/{id}/")
@permission_classes(
    [
        IsAuthenticated,
    ]
)
async def get_one(request: Request, id: int, Authorization: str = Header(...)):
    session = request.state.dbsession()
    repo = SqlAlchemyRepository(session, Post)
    instance = await repo.get(Post.id == id)
    await session.close()
    return instance


@router.put("/{id}/")
@permission_classes(
    [
        IsAuthenticated,
    ]
)
async def update_post(
    request: Request,
    id: int,
    data: UpdatePostSchema,
    Authorization: str = Header(...),
):
    session = request.state.dbsession()
    repo = SqlAlchemyRepository(session, Post)
    instance = await repo.update(id, **data.dict(exclude_none=True))
    await session.commit()
    await session.close()
    return instance


@router.delete("/{id}/", status_code=204)
@permission_classes(
    [
        IsAuthenticated,
    ]
)
async def delete_post(
    request: Request, id: int, Authorization: str = Header(...)
):
    await check_and_delete_post(id, request)
    return 204


@router.post("/{post_id}/like/", status_code=200)
@permission_classes(
    [
        IsAuthenticated,
    ]
)
async def like_post(
    request: Request, post_id: int, Authorization: str = Header(...)
):
    await user_like_post(post_id, request)
    return 200


@router.delete("/{post_id}/dislike/", status_code=204)
@permission_classes(
    [
        IsAuthenticated,
    ]
)
async def dislike_post(
    request: Request, post_id: int, Authorization: str = Header(...)
):
    await user_dislike_post(post_id, request)
    return 200
