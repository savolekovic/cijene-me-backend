from abc import ABC, abstractmethod
from typing import List, Optional
from decimal import Decimal
from app.domain.models.product.product_entry import ProductEntry

class ProductEntryRepository(ABC):
    @abstractmethod
    async def create(
        self, 
        product_id: int, 
        store_brand_id: int,
        store_location_id: int,
        price: Decimal
    ) -> ProductEntry:
        pass
    
    @abstractmethod
    async def get_all(self) -> List[ProductEntry]:
        pass
    
    @abstractmethod
    async def get(self, entry_id: int) -> Optional[ProductEntry]:
        pass

    @abstractmethod
    async def get_by_product(self, product_id: int) -> List[ProductEntry]:
        pass

    @abstractmethod
    async def get_by_store_brand(self, store_brand_id: int) -> List[ProductEntry]:
        pass

    @abstractmethod
    async def get_by_store_location(self, store_location_id: int) -> List[ProductEntry]:
        pass 