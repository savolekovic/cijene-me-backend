from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.infrastructure.database.database import Base, get_current_time

class ProductModel(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    barcode = Column(String, nullable=False, unique=True)
    image_url = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_current_time)
    
    # Add relationships
    category = relationship("CategoryModel", back_populates="products")
    product_entries = relationship("ProductEntryModel", back_populates="product") 