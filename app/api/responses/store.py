from datetime import datetime
from pydantic import BaseModel

class StoreBrandResponse(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True

class StoreLocationResponse(BaseModel):
    id: int
    store_brand_id: int
    address: str
    created_at: datetime

    class Config:
        from_attributes = True

class StoreLocationWithBrandResponse(StoreLocationResponse):
    store_brand_name: str 