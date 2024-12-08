from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
from app.infrastructure.database.database import Base

class CategoryModel(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Add relationship
    products = relationship("ProductModel", back_populates="category") 