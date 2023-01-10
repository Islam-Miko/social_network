from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    DATETIME
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.declarative import declared_attr


class Base:
    
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    
    id = Column(Integer, primary_key=True)
    created_at = Column(DATETIME(True), default=datetime.utcnow)
    updated_at = Column(DATETIME(True), onupdate=datetime.utcnow)
    deleted_at = Column(DATETIME(True), nullable=True)
    
BaseModel = declarative_base(cls=Base)
    

