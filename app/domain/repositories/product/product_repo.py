from abc import ABC, abstractmethod
from typing import List, Optional
from app.api.responses.product import ProductWithCategoryResponse
from app.domain.models.product import Product
from sqlalchemy.ext.asyncio import AsyncSession

class ProductRepository(ABC):
    @abstractmethod
    async def create(self, name: str, image_url: str, category_id: int, db: AsyncSession) -> Product:
        pass

    @abstractmethod
    async def get_all(self, db: AsyncSession) -> List[ProductWithCategoryResponse]:
        pass

    @abstractmethod
    async def get(self, product_id: int, db: AsyncSession) -> Optional[ProductWithCategoryResponse]:
        pass

    @abstractmethod
    async def update(self, product_id: int, product: Product, db: AsyncSession) -> Optional[Product]:
        pass

    @abstractmethod
    async def delete(self, product_id: int, db: AsyncSession) -> bool:
        pass

    @abstractmethod
    async def get_by_category(self, category_id: int, db: AsyncSession) -> List[Product]:
        pass