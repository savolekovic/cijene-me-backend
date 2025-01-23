from datetime import datetime
from pydantic import BaseModel
from typing import List
from app.api.responses.common import PaginatedResponse

class CategoryInProduct(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class ProductWithCategoryResponse(BaseModel):
    id: int
    name: str
    barcode: str
    image_url: str
    created_at: datetime
    category: CategoryInProduct

    class Config:
        from_attributes = True

class SimpleProductResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

# Use the generic PaginatedResponse with ProductWithCategoryResponse
PaginatedProductResponse = PaginatedResponse[ProductWithCategoryResponse]