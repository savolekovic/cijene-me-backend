from pydantic import BaseModel

class ProductRequest(BaseModel):
    name: str
    image_url: str
    category_id: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Jabuka",
                "image_url": "https://example.com/images/apple.jpg",
                "category_id": 1
            }
        }
 