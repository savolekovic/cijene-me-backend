from datetime import datetime
from pydantic import BaseModel, Field

class StoreBrand(BaseModel):
    id: int | None = None
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow) 