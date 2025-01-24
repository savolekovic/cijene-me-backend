from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.models.store.store_brand import StoreBrand
from app.infrastructure.database.models.store.store_location import StoreLocationModel
from app.api.responses.store import PaginatedStoreBrandResponse, SimpleStoreBrandResponse


class StoreBrandRepository(ABC):
    @abstractmethod
    async def create(self, name: str, db: AsyncSession) -> StoreBrand:
        pass
    
    @abstractmethod
    async def get(self, store_brand_id: int, db: AsyncSession) -> Optional[StoreBrand]:
        pass
    
    @abstractmethod
    async def get_all(self, db: AsyncSession, page: int = 1, per_page: int = 10, search: str = None) -> PaginatedStoreBrandResponse:
        """Get a paginated list of all store brands with optional search."""
        pass
    
    @abstractmethod
    async def update(self, store_brand_id: int, store_brand: StoreBrand, db: AsyncSession) -> Optional[StoreBrand]:
        pass
    
    @abstractmethod
    async def delete(self, store_brand_id: int, db: AsyncSession) -> bool:
        pass

    @abstractmethod
    async def get_by_name(self, name: str, db: AsyncSession) -> Optional[StoreBrand]:
        pass

    @abstractmethod
    async def get_locations_for_brand(self, store_brand_id: int, db: AsyncSession) -> List[StoreLocationModel]:
        """Get all store locations for a specific brand."""
        pass

    @abstractmethod
    async def get_all_simple(self, db: AsyncSession, search: str = None) -> List[SimpleStoreBrandResponse]:
        """Get a simplified list of all store brands with optional search."""
        pass