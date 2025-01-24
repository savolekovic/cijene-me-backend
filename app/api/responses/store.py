from datetime import datetime
from pydantic import BaseModel
from app.api.responses.common import PaginatedResponse

class StoreBrandResponse(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True

class SimpleStoreBrandResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class StoreBrandInLocation(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class StoreLocationResponse(BaseModel):
    id: int
    address: str
    created_at: datetime
    store_brand: StoreBrandInLocation

    class Config:
        from_attributes = True

class SimpleStoreLocationResponse(BaseModel):
    id: int
    address: str
    store_brand_name: str

    class Config:
        from_attributes = True

# Use the generic PaginatedResponse with StoreBrandResponse
PaginatedStoreBrandResponse = PaginatedResponse[StoreBrandResponse]

# Use the generic PaginatedResponse with StoreLocationResponse
PaginatedStoreLocationResponse = PaginatedResponse[StoreLocationResponse] 