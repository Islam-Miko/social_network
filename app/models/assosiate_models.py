from sqlalchemy import Column, ForeignKey, Table

from app.models.base_model import BaseAbstractModel

Like = Table(
    "sn_like",
    BaseAbstractModel.metadata,
    Column("post_id", ForeignKey("sn_post.id"), primary_key=True),
    Column("user_id", ForeignKey("sn_user.id"), primary_key=True),
)
