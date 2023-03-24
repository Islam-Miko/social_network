from pydantic import BaseModel


class BaseSchema(BaseModel):
    id: int


class PaginationSchema(BaseModel):
    data: list[BaseSchema]
    limit: int
    offset: int
    count: int
