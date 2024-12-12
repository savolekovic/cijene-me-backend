from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from app.infrastructure.database.database import get_current_time

class ProductEntry(BaseModel):
    id: int | None = None
    product_id: int
    store_brand_id: int
    store_location_id: int
    price: Decimal
    created_at: datetime = Field(default_factory=get_current_time) 