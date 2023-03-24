from fastapi import Depends

from app.repositories.like_repository import LikeRepository


class LikeService:
    repository: LikeRepository

    def __init__(self, repository: LikeRepository = Depends()) -> None:
        self.repository = repository

    async def like(self, post_id: int, user_id: int) -> int:
        return await self.repository.like_post(post_id, user_id)

    async def dislike(self, post_id: int, user_id: int) -> None:
        return await self.repository.dislike_post(post_id, user_id)
