from datetime import datetime
from pydantic import BaseModel, Field

class Product(BaseModel):
    id: int | None = None
    name: str
    image_url: str
    category_id: int
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ProductWithCategory(Product):
    category_name: str 