from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.models.store.store_location import StoreLocation
from sqlalchemy.ext.asyncio import AsyncSession


class StoreLocationRepository(ABC):
    @abstractmethod
    async def create(self, store_brand_id: int, address: str, db: AsyncSession) -> StoreLocation:
        pass
    
    @abstractmethod
    async def get(self, location_id: int, db: AsyncSession) -> Optional[StoreLocation]:
        pass
    
    @abstractmethod
    async def get_all(self, db: AsyncSession) -> List[StoreLocation]:
        pass
    
    @abstractmethod
    async def get_by_store_brand(self, store_brand_id: int, db: AsyncSession) -> List[StoreLocation]:
        pass
    
    @abstractmethod
    async def update(self, location_id: int, store_location: StoreLocation, db: AsyncSession) -> Optional[StoreLocation]:
        pass
    
    @abstractmethod
    async def delete(self, location_id: int, db: AsyncSession) -> bool:
        pass 