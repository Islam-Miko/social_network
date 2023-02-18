from collections.abc import Set
from datetime import date

from sqlalchemy import DATE, Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.assosiate_models import Like
from app.models.base_model import BaseAbstractModel


class User(BaseAbstractModel):
    __tablename__ = "sn_user"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    birth_date: Mapped[date] = mapped_column(DATE, nullable=False)

    credentials: Mapped["Credential"] = relationship(back_populates="user")
    likes: Mapped[Set["Post"]] = relationship(  # noqa
        secondary=Like, back_populates="liked_users"
    )


class Credential(BaseAbstractModel):
    __tablename__ = "sn_credential"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("sn_user.id"), unique=True)
    login: Mapped[str] = mapped_column(String(50), nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    user: Mapped["User"] = relationship(back_populates="credentials")


class RefreshToken(BaseAbstractModel):
    __tablename__ = "sn_refresh_token"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(255), nullable=False)
    valid_until: Mapped[float] = mapped_column(Float, nullable=False)
    owner: Mapped[int] = Column(
        Integer, ForeignKey("sn_user.id", ondelete="CASCADE")
    )
