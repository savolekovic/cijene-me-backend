from abc import ABC, abstractmethod
from typing import List, Optional
from decimal import Decimal
from app.api.responses.product_entry import ProductEntryWithDetails, PaginatedProductEntryResponse
from app.domain.models.product.product_entry import ProductEntry
from sqlalchemy.ext.asyncio import AsyncSession

class ProductEntryRepository(ABC):
    @abstractmethod
    async def create(
        self, 
        product_id: int, 
        store_brand_id: int,
        store_location_id: int,
        price: Decimal,
        db: AsyncSession
    ) -> ProductEntryWithDetails:
        pass
    
    @abstractmethod
    async def get_all(self, db: AsyncSession, page: int = 1, per_page: int = 10, search: str = None, order_by: str = "created_at", order_direction: str = "desc") -> PaginatedProductEntryResponse:
        """Get a paginated list of all product entries with optional search and ordering."""
        pass
    
    @abstractmethod
    async def get(self, entry_id: int, db: AsyncSession) -> Optional[ProductEntry]:
        pass

    @abstractmethod
    async def get_by_product(self, product_id: int, db: AsyncSession) -> List[ProductEntry]:
        pass

    @abstractmethod
    async def get_by_store_brand(self, store_brand_id: int, db: AsyncSession) -> List[ProductEntry]:
        pass

    @abstractmethod
    async def get_by_store_location(self, store_location_id: int, db: AsyncSession) -> List[ProductEntry]:
        pass 

    @abstractmethod
    async def delete(self, entry_id: int, db: AsyncSession) -> bool:
        pass 