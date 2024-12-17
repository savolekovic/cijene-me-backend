from datetime import datetime
from pydantic import BaseModel

class StoreBrandResponse(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True

class StoreBrandInLocation(BaseModel):
    id: int
    name: str

class StoreLocationResponse(BaseModel):
    id: int
    address: str
    created_at: datetime
    store_brand: StoreBrandInLocation

    class Config:
        from_attributes = True 