from datetime import datetime
from pydantic import BaseModel, Field

class Category(BaseModel):
    id: int | None = None
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow) 

# Add request model
class CategoryCreate(BaseModel):
    name: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Voće i Povrće"
            }
        }
