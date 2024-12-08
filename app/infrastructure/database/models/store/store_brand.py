from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
from app.infrastructure.database.database import Base

class StoreBrandModel(Base):
    __tablename__ = "store_brands"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Add relationship
    locations = relationship("StoreLocationModel", back_populates="store_brand")
    product_entries = relationship("ProductEntryModel", back_populates="store_brand")