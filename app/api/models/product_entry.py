from pydantic import BaseModel
from decimal import Decimal

class ProductEntryRequest(BaseModel):
    product_id: int
    store_location_id: int
    price: Decimal

    class Config:
        json_schema_extra = {
            "example": {
                "product_id": 1,
                "store_location_id": 1,
                "price": "9.99"
            }
        } 