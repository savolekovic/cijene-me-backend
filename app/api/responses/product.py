from datetime import datetime
from pydantic import BaseModel

class ProductResponse(BaseModel):
    id: int
    name: str
    image_url: str
    category_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ProductWithCategoryResponse(ProductResponse):
    category_name: str 