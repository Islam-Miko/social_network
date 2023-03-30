from fastapi import APIRouter, Depends, Request

from app.dependencies import check_authenticated
from app.schemas.post_schema import (
    PostCreateSchema,
    PostPaginationSchema,
    PostSchema,
    UpdatePostSchema,
)
from app.services.post_service import LikeService, PostService

router = APIRouter(
    prefix="/posts", dependencies=[Depends(check_authenticated)]
)


@router.get("/", response_model=PostPaginationSchema)
async def get_posts(
    offset: int = 0, limit: int = 20, service: PostService = Depends()
):
    return await service.get_list(offset, limit)


@router.post("/", status_code=201)
async def create_post(
    request: Request, data: PostCreateSchema, service: PostService = Depends()
):
    return await service.create_post(data, request)


@router.get("/{id}/", response_model=PostSchema)
async def get_one(id: int, service: PostService = Depends()):
    return await service.get_one(id)


@router.put("/{id}/", response_model=PostSchema)
async def update_post(
    id: int, data: UpdatePostSchema, service: PostService = Depends()
):
    return await service.update(id, data)


@router.delete("/{id}/", status_code=204)
async def delete_post(
    request: Request, id: int, service: PostService = Depends()
):
    await service.check_and_delete_post(id, request.user.id)
    return 204


@router.post("/{post_id}/like/", status_code=200)
async def like_post(
    request: Request,
    post_id: int,
    service: PostService = Depends(),
    like_service: LikeService = Depends(),
):
    await service.like_post(post_id, request.user.id, like_service)
    return 200


@router.delete("/{post_id}/dislike/", status_code=204)
async def dislike_post(
    request: Request,
    post_id: int,
    service: PostService = Depends(),
    like_service: LikeService = Depends(),
):
    await service.dislike_post(post_id, request.user.id, like_service)
    return 200
