from datetime import datetime
from pydantic import BaseModel

from app.api.responses.common import PaginatedResponse

class CategoryResponse(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True 
        
# Use the generic PaginatedResponse with CategoryResponse for category listing
PaginatedCategoryResponse = PaginatedResponse[CategoryResponse]