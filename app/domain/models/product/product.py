from datetime import datetime
from pydantic import BaseModel, Field
from app.infrastructure.database.database import get_current_time

class Product(BaseModel):
    id: int | None = None
    name: str
    barcode: str
    image_url: str
    category_id: int
    created_at: datetime = Field(default_factory=get_current_time)

class ProductWithCategory(Product):
    category_name: str 