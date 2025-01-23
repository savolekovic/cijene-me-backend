from typing import List, TypeVar, Generic
from pydantic import BaseModel

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    total_count: int
    data: List[T]

    class Config:
        from_attributes = True 