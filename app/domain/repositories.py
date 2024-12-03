from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from .models import StoreBrand

class StoreBrandRepository(ABC):
    @abstractmethod
    async def create(self, store_brand: StoreBrand) -> StoreBrand:
        pass
    
    @abstractmethod
    async def get_by_id(self, store_brand_id: UUID) -> Optional[StoreBrand]:
        pass
    
    @abstractmethod
    async def get_all(self) -> List[StoreBrand]:
        pass
    
    @abstractmethod
    async def update(self, store_brand_id: UUID, store_brand: StoreBrand) -> Optional[StoreBrand]:
        pass
    
    @abstractmethod
    async def delete(self, store_brand_id: UUID) -> bool:
        pass 