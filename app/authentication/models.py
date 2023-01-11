from sqlalchemy import DATE, Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, backref, relationship

from ..base.models import BaseModel


class User(BaseModel):
    __tablename__ = "webtronics_user"

    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    birth_date = Column(DATE, nullable=False)
    credentials: Mapped["Credential"] = relationship(
        "Credential", backref=backref("user", uselist=False, lazy="subquery")
    )


class Credential(BaseModel):
    __tablename__ = "webtronics_credential"

    id = Column(Integer, ForeignKey("webtronics_user.id"), primary_key=True)
    login = Column(String(50), nullable=False)
    password = Column(String(255), nullable=False)


class RefreshToken(BaseModel):
    __tablename__ = "webtronics_refresh_token"

    key = Column(String(255), nullable=False)
    valid_until = Column(Float, nullable=False)
    owner = Column(
        Integer, ForeignKey("webtronics_user.id", ondelete="CASCADE")
    )
