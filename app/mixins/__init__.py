from typing import Dict, Sequence

from sqlalchemy import BaseRow

from app.repositories.base_repository import BaseSqlAlchemyRepository
from app.schemas.post_schema import PostSchema


class PaginationMixin:

    repository: BaseSqlAlchemyRepository

    async def get_paginated(
        self, offset: int = 0, limit: int = 20, *clauses: Sequence
    ) -> Dict:
        count = await self.repository.count(*clauses)
        data: Sequence[BaseRow] = await self.repository.all(
            limit, offset, *clauses
        )
        return {
            "count": count,
            "limit": limit,
            "offset": offset,
            "data": [PostSchema.from_orm(item).dict() for item in data],
        }
