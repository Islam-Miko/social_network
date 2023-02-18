from app.models.post_model import Post
from app.repositories.base_repository import BaseSqlAlchemyRepository


class PostRepository(BaseSqlAlchemyRepository):
    model = Post
