from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from app.infrastructure.database.database import Base, get_current_time

class ProductEntryModel(Base):
    __tablename__ = "product_entries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    store_brand_id = Column(Integer, ForeignKey("store_brands.id", ondelete="CASCADE"), nullable=False)
    store_location_id = Column(Integer, ForeignKey("store_locations.id", ondelete="CASCADE"), nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_current_time)
    
    # Add relationships
    product = relationship("ProductModel", back_populates="product_entries")
    store_brand = relationship("StoreBrandModel", back_populates="product_entries")
    store_location = relationship("StoreLocationModel", back_populates="product_entries") 