from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.models.store.store_brand import StoreBrand
from sqlalchemy.ext.asyncio import AsyncSession


class StoreBrandRepository(ABC):
    @abstractmethod
    async def create(self, name: str, db: AsyncSession) -> StoreBrand:
        pass
    
    @abstractmethod
    async def get(self, store_brand_id: int, db: AsyncSession) -> Optional[StoreBrand]:
        pass
    
    @abstractmethod
    async def get_all(self, db: AsyncSession) -> List[StoreBrand]:
        pass
    
    @abstractmethod
    async def update(self, store_brand_id: int, store_brand: StoreBrand, db: AsyncSession) -> Optional[StoreBrand]:
        pass
    
    @abstractmethod
    async def delete(self, store_brand_id: int, db: AsyncSession) -> bool:
        pass