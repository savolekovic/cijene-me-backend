from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.infrastructure.database.database import get_current_time

class Category(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int | None = None
    name: str
    created_at: datetime = Field(default_factory=get_current_time)

