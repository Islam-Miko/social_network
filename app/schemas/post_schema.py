from typing import Optional

from app.schemas.base_schema import BaseSchema, PaginationSchema


class PostCreateSchema(BaseSchema):
    id: Optional[int]
    header: str
    body: str


class PostSchema(PostCreateSchema):
    id: int


class UpdatePostSchema(PostCreateSchema):
    header: Optional[str]
    body: Optional[str]


class PostPaginationSchema(PaginationSchema):
    data: list[PostSchema]
