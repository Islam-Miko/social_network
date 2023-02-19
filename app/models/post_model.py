from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.assosiate_models import Like
from app.models.base_model import BaseAbstractModel


class Post(BaseAbstractModel):
    __tablename__ = "sn_post"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    header: Mapped[str] = mapped_column(String(100), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    owner: Mapped[int] = mapped_column(Integer, ForeignKey("sn_user.id"))

    liked_users: Mapped[set["User"]] = relationship(  # noqa
        secondary=Like, back_populates="likes"
    )
