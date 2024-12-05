from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.models import StoreBrand

class StoreBrandRepository(ABC):
    @abstractmethod
    async def create(self, name: str) -> StoreBrand:
        pass
    
    @abstractmethod
    async def get(self, store_brand_id: int) -> Optional[StoreBrand]:
        pass
    
    @abstractmethod
    async def get_all(self) -> List[StoreBrand]:
        pass
    
    @abstractmethod
    async def update(self, store_brand_id: int, store_brand: StoreBrand) -> Optional[StoreBrand]:
        pass
    
    @abstractmethod
    async def delete(self, store_brand_id: int) -> bool:
        pass 