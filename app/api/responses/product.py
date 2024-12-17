from datetime import datetime
from pydantic import BaseModel

class CategoryInProduct(BaseModel):
    id: int
    name: str

class ProductWithCategoryResponse(BaseModel):
    id: int
    name: str
    image_url: str
    created_at: datetime
    category: CategoryInProduct

    class Config:
        from_attributes = True