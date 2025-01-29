from abc import ABC, abstractmethod
from typing import List, Optional
from app.api.responses.product import ProductWithCategoryResponse, PaginatedProductResponse, SimpleProductResponse
from app.domain.models.product import Product
from sqlalchemy.ext.asyncio import AsyncSession

class ProductRepository(ABC):
    @abstractmethod
    async def create(self, name: str, barcode: str, image_url: str, category_id: int, db: AsyncSession) -> Product:
        pass

    @abstractmethod
    async def get_all(
        self, 
        db: AsyncSession, 
        page: int = 1, 
        per_page: int = 10, 
        search: str = None,
        category_id: int = None,
        has_entries: bool = None,
        min_price: float = None,
        max_price: float = None,
        barcode: str = None,
        order_by: str = "name", 
        order_direction: str = "asc"
    ) -> PaginatedProductResponse:
        """Get a paginated list of all products with optional search, filtering and ordering.
        
        Args:
            db: Database session
            page: Page number (default: 1)
            per_page: Number of items per page (default: 10)
            search: Optional search query
            category_id: Optional category ID filter
            has_entries: Filter products that have/don't have price entries
            min_price: Minimum current price filter
            max_price: Maximum current price filter
            barcode: Filter by exact barcode match
            order_by: Field to order by (default: name)
            order_direction: Order direction (asc or desc) (default: asc)
        """
        pass

    @abstractmethod
    async def get_all_simple(self, db: AsyncSession, search: str = None) -> List[SimpleProductResponse]:
        """Get a simplified list of all products with only id and name."""
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
    
    @abstractmethod
    async def get_by_name(self, name: str, db: AsyncSession) -> Optional[Product]:
        pass
    
    @abstractmethod
    async def get_by_barcode(self, barcode: str, db: AsyncSession) -> Optional[Product]:
        pass