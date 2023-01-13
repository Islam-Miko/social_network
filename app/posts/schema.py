from typing import Optional

from pydantic import BaseModel

from ..base.schema import BaseSchema


class PostCreateSchema(BaseModel):
    header: str
    body: str


class PostSchema(BaseSchema, PostCreateSchema):
    ...


class UpdatePostSchema(PostSchema):
    header: Optional[str]
    body: Optional[str]
    id: Optional[int]
