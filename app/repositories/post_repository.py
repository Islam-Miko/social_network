from sqlalchemy import select

from app.models.post_model import Post
from app.repositories.base_repository import BaseSqlAlchemyRepository


class PostRepository(BaseSqlAlchemyRepository):
    model = Post
    base_select = select(Post).where(Post.deleted_at.is_(None))
