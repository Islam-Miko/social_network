from sqlalchemy import Column, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import relationship

from ..base.models import BaseModel

Like = Table(
    "webtronics_like",
    BaseModel.metadata,
    Column("post_id", ForeignKey("webtronics_post.id"), primary_key=True),
    Column("user_id", ForeignKey("webtronics_user.id"), primary_key=True),
)


class Post(BaseModel):
    __tablename__ = "webtronics_post"

    header = Column(String(100), nullable=False)
    body = Column(Text, nullable=False)
    owner = Column(Integer, ForeignKey("webtronics_user.id"))
    liked_users = relationship("User", secondary=Like, backref="self_likes")
