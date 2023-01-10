from datetime import datetime

from sqlalchemy import DATETIME, Column, Integer
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import declarative_base


class Base:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)
    created_at = Column(DATETIME(True), default=datetime.utcnow)
    updated_at = Column(DATETIME(True), onupdate=datetime.utcnow)
    deleted_at = Column(DATETIME(True), nullable=True)


BaseModel = declarative_base(cls=Base)
