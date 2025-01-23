from datetime import datetime
from pydantic import BaseModel
from decimal import Decimal
from app.api.responses.common import PaginatedResponse
from app.api.responses.product import ProductWithCategoryResponse

class ProductInEntry(BaseModel):
    id: int
    name: str
    barcode: str

class StoreBrandInEntry(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class StoreLocationInEntry(BaseModel):
    id: int
    address: str
    store_brand: StoreBrandInEntry

    class Config:
        from_attributes = True

class ProductEntryWithDetails(BaseModel):
    id: int
    price: Decimal
    created_at: datetime
    product: ProductWithCategoryResponse
    store_location: StoreLocationInEntry

    class Config:
        from_attributes = True

# Use the generic PaginatedResponse with ProductEntryWithDetails
PaginatedProductEntryResponse = PaginatedResponse[ProductEntryWithDetails] 