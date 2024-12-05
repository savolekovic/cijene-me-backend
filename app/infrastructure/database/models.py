from sqlalchemy import Column, String, DateTime, Integer
from datetime import datetime
from .database import Base

class StoreBrandModel(Base):
    __tablename__ = "store_brands"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow) 