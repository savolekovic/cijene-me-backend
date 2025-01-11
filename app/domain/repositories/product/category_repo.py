from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.models.product.category import Category
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.models.product import ProductModel

class CategoryRepository(ABC):
    @abstractmethod
    async def create(self, name: str, db: AsyncSession) -> Category:
        pass
    
    @abstractmethod
    async def get_all(self, db: AsyncSession) -> List[Category]:
        pass
    
    @abstractmethod
    async def get(self, category_id: int, db: AsyncSession) -> Optional[Category]:
        pass

    @abstractmethod
    async def update(self, category_id: int, category: Category, db: AsyncSession) -> Optional[Category]:
        pass

    @abstractmethod
    async def delete(self, category_id: int, db: AsyncSession) -> bool:
        pass

    @abstractmethod
    async def get_products_in_category(self, category_id: int, db: AsyncSession) -> List[ProductModel]:
        pass