from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.models.store_location import StoreLocation


class StoreLocationRepository(ABC):
    @abstractmethod
    async def create(self, store_brand_id: int, address: str) -> StoreLocation:
        pass
    
    @abstractmethod
    async def get(self, location_id: int) -> Optional[StoreLocation]:
        pass
    
    @abstractmethod
    async def get_all(self) -> List[StoreLocation]:
        pass
    
    @abstractmethod
    async def get_by_store_brand(self, store_brand_id: int) -> List[StoreLocation]:
        pass
    
    @abstractmethod
    async def update(self, location_id: int, store_location: StoreLocation) -> Optional[StoreLocation]:
        pass
    
    @abstractmethod
    async def delete(self, location_id: int) -> bool:
        pass 