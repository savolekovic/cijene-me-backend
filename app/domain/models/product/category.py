from datetime import datetime
from pydantic import BaseModel, Field
from app.infrastructure.database.database import get_current_time

class Category(BaseModel):
    id: int | None = None
    name: str
    created_at: datetime = Field(default_factory=get_current_time) 

# Add request model
class CategoryCreate(BaseModel):
    name: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Voće i Povrće"
            }
        }
