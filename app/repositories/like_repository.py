from sqlalchemy import delete, insert

from app.models.post_model import Like
from app.repositories.base_repository import BaseSqlAlchemyRepository


class LikeRepository(BaseSqlAlchemyRepository):
    model = Like

    async def like_post(self, post_id: int, user_id: int) -> None:
        stmt = insert(Like).values(user_id=user_id, post_id=post_id)
        await self.session.execute(stmt)
        await self.session.commit()

    async def dislike_post(
        self,
        post_id: int,
        user_id: int,
    ) -> None:
        stmt = delete(Like).where(
            Like.c.user_id == user_id, Like.c.post_id == post_id
        )
        await self.session.execute(stmt)
        await self.session.commit()
