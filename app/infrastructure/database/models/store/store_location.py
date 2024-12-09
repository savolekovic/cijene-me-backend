from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.infrastructure.database.database import Base, get_current_time

class StoreLocationModel(Base):
    __tablename__ = "store_locations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    store_brand_id = Column(Integer, ForeignKey("store_brands.id"), nullable=False)
    address = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_current_time)
    
    # Add relationships
    store_brand = relationship("StoreBrandModel", back_populates="locations")
    product_entries = relationship("ProductEntryModel", back_populates="store_location")
  