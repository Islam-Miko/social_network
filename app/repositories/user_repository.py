from app.models.user_model import User
from app.repositories.base_repository import BaseSqlAlchemyRepository


class UserRepository(BaseSqlAlchemyRepository):
    model = User
