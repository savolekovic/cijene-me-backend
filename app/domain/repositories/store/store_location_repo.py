from abc import ABC, abstractmethod
from typing import List, Optional
from app.api.responses.store import StoreLocationResponse, PaginatedStoreLocationResponse
from app.domain.models.store.store_location import StoreLocation
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.models.product import ProductEntryModel


class StoreLocationRepository(ABC):
    @abstractmethod
    async def create(self, address: str, store_brand_id: int, db: AsyncSession) -> StoreLocationResponse:
        """Create a new store location."""
        pass
    
    @abstractmethod
    async def get(self, location_id: int, db: AsyncSession) -> Optional[StoreLocationResponse]:
        """Get a store location by ID."""
        pass
    
    @abstractmethod
    async def get_all(self, db: AsyncSession, page: int = 1, per_page: int = 10, search: str = None) -> PaginatedStoreLocationResponse:
        """Get a paginated list of all store locations with optional search."""
        pass
    
    @abstractmethod
    async def get_by_store_brand(self, store_brand_id: int, db: AsyncSession) -> List[StoreLocation]:
        """Get all store locations for a specific brand."""
        pass
    
    @abstractmethod
    async def update(self, location_id: int, location: StoreLocation, db: AsyncSession) -> Optional[StoreLocationResponse]:
        """Update a store location."""
        pass
    
    @abstractmethod
    async def delete(self, location_id: int, db: AsyncSession) -> bool:
        """Delete a store location."""
        pass
    
    @abstractmethod
    async def get_product_entries_for_location(self, store_location_id: int, db: AsyncSession) -> List[ProductEntryModel]:
        pass 