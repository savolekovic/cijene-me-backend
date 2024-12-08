from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field

class ProductEntry(BaseModel):
    id: int | None = None
    product_id: int
    store_brand_id: int
    store_location_id: int
    price: Decimal
    created_at: datetime = Field(default_factory=datetime.utcnow) 