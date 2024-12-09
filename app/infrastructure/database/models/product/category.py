from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.orm import relationship
from app.infrastructure.database.database import Base, get_current_time

class CategoryModel(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_current_time)
    
    # Add relationship
    products = relationship("ProductModel", back_populates="category") 