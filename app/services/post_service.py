from datetime import datetime
from typing import Sequence

from fastapi import Depends, HTTPException, Request

from app import messages
from app.mixins import PaginationMixin
from app.models.post_model import Post
from app.repositories.post_repository import PostRepository
from app.schemas.post_schema import (
    PostCreateSchema,
    PostSchema,
    UpdatePostSchema,
)
from app.services.like_service import LikeService


class PostService(PaginationMixin):
    repository: PostRepository

    def __init__(self, repository: PostRepository = Depends()) -> None:
        self.repository = repository

    async def delete_post(self, id: int) -> None:
        await self.repository.update(id, {"deleted_at": datetime.now()})

    async def check_post_owner(self, id: int, user_id: int) -> bool:
        return await self.repository.exists(
            Post.id == id, Post.owner == user_id
        )

    async def check_self_post(self, id: int, user_id: int) -> None:
        is_owner = await self.check_post_owner(id, user_id)
        if is_owner:
            raise HTTPException(
                status_code=400,
                detail=messages.ACTION_NOT_ALLOWED,
            )

    async def check_and_delete_post(self, id: int, user_id: int) -> None:
        is_owner = await self.check_post_owner(id, user_id)
        if not is_owner:
            raise HTTPException(
                status_code=400,
                detail=messages.ACTION_NOT_ALLOWED,
            )
        await self.delete_post(id)

    async def like_post(
        self, id: int, user_id: int, like_service: LikeService
    ) -> None:
        await self.check_self_post(id, user_id)
        await like_service.like(id, user_id)

    async def dislike_post(
        self, id: int, user_id: int, like_service: LikeService
    ) -> None:
        await self.check_self_post(id, user_id)
        await like_service.dislike(id, user_id)

    async def get_list(self, offset: int, limit: int, *args: Sequence):
        return await self.get_paginated(offset, limit, *args)

    async def create_post(self, data: PostCreateSchema, request: Request):
        data_dict = data.dict(exclude_none=True)
        data_dict.update({"owner": request.user.id})
        return await self.repository.create(data_dict)

    async def get_one(self, id: int) -> PostSchema:
        return await self.repository.get(id)

    async def update(self, id: int, data: UpdatePostSchema) -> Post:
        return await self.repository.update(id, data.dict(exclude_none=True))
