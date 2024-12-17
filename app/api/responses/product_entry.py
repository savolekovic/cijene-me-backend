from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel
from typing import List

class ProductEntryWithDetails(BaseModel):
    id: int
    price: Decimal
    created_at: datetime
    product_id: int
    product_name: str
    store_location_id: int
    store_location_address: str
    store_brand_id: int
    store_brand_name: str 