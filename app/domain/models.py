from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID, uuid4

class StoreBrand(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow) 