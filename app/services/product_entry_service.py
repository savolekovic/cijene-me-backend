from app.api.responses.product_entry import ProductEntryWithDetails, PaginatedProductEntryResponse
from app.domain.repositories.product.product_entry_repo import ProductEntryRepository
from app.domain.repositories.store.store_location_repo import StoreLocationRepository
from app.services.cache_service import CacheManager
from app.domain.models.product import ProductEntry
from app.infrastructure.logging.logger import get_logger
from app.core.exceptions import NotFoundError
from typing import List
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.repositories.product.postgres_product_entry_repository import PostgresProductEntryRepository

logger = get_logger(__name__)

class ProductEntryService:
    def __init__(
        self,
        store_location_repo: StoreLocationRepository,
        cache_manager: CacheManager,
        product_entry_repo: ProductEntryRepository = PostgresProductEntryRepository()
    ):
        self.product_entry_repo = product_entry_repo
        self.store_location_repo = store_location_repo
        self.cache_manager = cache_manager

    async def create_product_entry(
        self, 
        product_id: int,
        store_location_id: int,
        price: Decimal,
        db: AsyncSession
    ) -> ProductEntryWithDetails:
        try:
            # Get store location to verify it exists and get store_brand_id
            store_location = await self.store_location_repo.get(store_location_id, db)
            if not store_location:
                raise NotFoundError("Store Location", store_location_id)

            # Create entry with store_brand_id from the location's store_brand
            entry = await self.product_entry_repo.create(
                product_id=product_id,
                store_brand_id=store_location.store_brand.id,
                store_location_id=store_location_id,
                price=price,
                db=db
            )
            await self.cache_manager.clear_product_related_caches()
            return entry
        except Exception as e:
            logger.error(f"Error creating product entry: {str(e)}")
            raise

    async def get_all_product_entries(
        self, 
        db: AsyncSession, 
        page: int = 1, 
        per_page: int = 10,
        search: str = None
    ) -> PaginatedProductEntryResponse:
        """
        Get all product entries with pagination and optional search.
        
        Args:
            db: Database session
            page: Page number (default: 1)
            per_page: Number of items per page (default: 10)
            search: Optional search query
            
        Returns:
            PaginatedProductEntryResponse containing the paginated list of product entries
        """
        logger.info(f"Getting product entries - page: {page}, per_page: {per_page}, search: {search}")
        return await self.product_entry_repo.get_all(db, page=page, per_page=per_page, search=search)

    async def get_entry(self, entry_id: int, db: AsyncSession) -> ProductEntryWithDetails:
        try:
            logger.info(f"Fetching price entry with id: {entry_id}")
            entry = await self.product_entry_repo.get(entry_id, db)
            if not entry:
                logger.warning(f"Price entry not found: {entry_id}")
                raise NotFoundError("Price entry", entry_id)
            return entry
        except Exception as e:
            logger.error(f"Error fetching price entry {entry_id}: {str(e)}")
            raise

    async def get_entries_by_product(self, product_id: int, db: AsyncSession) -> List[ProductEntryWithDetails]:
        try:
            logger.info(f"Fetching price entries for product: {product_id}")
            return await self.product_entry_repo.get_by_product(product_id, db)
        except Exception as e:
            logger.error(f"Error fetching price entries for product {product_id}: {str(e)}")
            raise

    async def get_entries_by_store_brand(self, store_brand_id: int, db: AsyncSession) -> List[ProductEntryWithDetails]:
        try:
            logger.info(f"Fetching price entries for store brand: {store_brand_id}")
            return await self.product_entry_repo.get_by_store_brand(store_brand_id, db)
        except Exception as e:
            logger.error(f"Error fetching price entries for store brand {store_brand_id}: {str(e)}")
            raise

    async def get_entries_by_store_location(self, store_location_id: int, db: AsyncSession) -> List[ProductEntryWithDetails]:
        try:
            logger.info(f"Fetching price entries for store location: {store_location_id}")
            return await self.product_entry_repo.get_by_store_location(store_location_id, db)
        except Exception as e:
            logger.error(f"Error fetching price entries for store location {store_location_id}: {str(e)}")
            raise

    async def delete_entry(self, entry_id: int, db: AsyncSession) -> bool:
        try:
            logger.info(f"Attempting to delete product entry {entry_id}")
            
            # First check if entry exists
            entry = await self.product_entry_repo.get(entry_id, db)
            if not entry:
                logger.warning(f"Product entry not found: {entry_id}")
                raise NotFoundError("Product entry", entry_id)
            
            success = await self.product_entry_repo.delete(entry_id, db)
            logger.info(f"Successfully deleted product entry {entry_id}")
            await self.cache_manager.clear_product_related_caches()
            return True
        except Exception as e:
            logger.error(f"Error deleting product entry {entry_id}: {str(e)}")
            raise
