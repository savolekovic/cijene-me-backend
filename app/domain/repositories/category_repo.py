from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.models.product.category import Category

class CategoryRepository(ABC):
    @abstractmethod
    async def create(self, name: str) -> Category:
        pass
    
    @abstractmethod
    async def get_all(self) -> List[Category]:
        pass
    
    @abstractmethod
    async def get(self, category_id: int) -> Optional[Category]:
        pass 