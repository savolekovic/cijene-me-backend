from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel

class ProductInEntry(BaseModel):
    id: int
    name: str

class StoreBrandInEntry(BaseModel):
    id: int
    name: str

class StoreLocationInEntry(BaseModel):
    id: int
    address: str
    store_brand: StoreBrandInEntry

class ProductEntryWithDetails(BaseModel):
    id: int
    price: Decimal
    created_at: datetime
    product: ProductInEntry
    store_location: StoreLocationInEntry 