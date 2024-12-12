from pydantic import BaseModel

class StoreBrandRequest(BaseModel):
    name: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "IDEA"
            }
        }

class StoreLocationRequest(BaseModel):
    store_brand_id: int
    address: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "store_brand_id": 1,
                "address": "Bulevar Džordža Vašingtona 12"
            }
        } 