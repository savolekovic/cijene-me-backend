from datetime import datetime
from pydantic import BaseModel
from decimal import Decimal
from app.api.responses.common import PaginatedResponse

class ProductInEntry(BaseModel):
    id: int
    name: str
    image_url: str

    class Config:
        from_attributes = True

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
    product: ProductInEntry
    store_location: StoreLocationInEntry

    class Config:
        from_attributes = True

class ProductPriceStatistics(BaseModel):
    lowest_price: float | None
    highest_price: float | None
    average_price: float | None
    latest_price: float | None
    total_entries: int
    first_entry_date: datetime | None
    latest_entry_date: datetime | None
    price_change: float | None
    price_change_percentage: float | None

    class Config:
        from_attributes = True

# Use the generic PaginatedResponse with ProductEntryWithDetails
PaginatedProductEntryResponse = PaginatedResponse[ProductEntryWithDetails] 