from datetime import datetime
from pydantic import BaseModel, Field


class StoreLocation(BaseModel):
    id: int | None = None
    store_brand_id: int
    address: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
  
  