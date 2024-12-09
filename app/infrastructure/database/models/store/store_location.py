from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.infrastructure.database.database import Base

class StoreLocationModel(Base):
    __tablename__ = "store_locations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    store_brand_id = Column(Integer, ForeignKey("store_brands.id"), nullable=False)
    address = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Add relationship
    store_brand = relationship("StoreBrandModel", back_populates="locations")
  