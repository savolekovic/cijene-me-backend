from app.domain.repositories.product.product_entry_repo import ProductEntryRepository
from app.services.cache_service import CacheManager
from app.domain.models.product import ProductEntry
from app.infrastructure.logging.logger import get_logger
from app.core.exceptions import NotFoundError
from typing import List
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger(__name__)

class ProductEntryService:
    def __init__(self, product_entry_repo: ProductEntryRepository, cache_manager: CacheManager):
        self.product_entry_repo = product_entry_repo
        self.cache_manager = cache_manager

    async def create_entry(
        self, 
        product_id: int,
        store_brand_id: int,
        store_location_id: int,
        price: Decimal,
        db: AsyncSession
    ) -> ProductEntry:
        try:
            logger.info(f"Creating new price entry for product {product_id}")
            entry = await self.product_entry_repo.create(
                product_id=product_id,
                store_brand_id=store_brand_id,
                store_location_id=store_location_id,
                price=price,
                db=db
            )
            logger.info(f"Created price entry with id: {entry.id}")
            await self.cache_manager.clear_product_related_caches()
            return entry
        except Exception as e:
            logger.error(f"Error creating price entry: {str(e)}")
            raise

    async def get_all_entries(self, db: AsyncSession) -> List[ProductEntry]:
        try:
            logger.info("Fetching all price entries")
            return await self.product_entry_repo.get_all(db)
        except Exception as e:
            logger.error(f"Error fetching price entries: {str(e)}")
            raise

    async def get_entry(self, entry_id: int, db: AsyncSession) -> ProductEntry:
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

    async def get_entries_by_product(self, product_id: int, db: AsyncSession) -> List[ProductEntry]:
        try:
            logger.info(f"Fetching price entries for product: {product_id}")
            return await self.product_entry_repo.get_by_product(product_id, db)
        except Exception as e:
            logger.error(f"Error fetching price entries for product {product_id}: {str(e)}")
            raise

    async def get_entries_by_store_brand(self, store_brand_id: int, db: AsyncSession) -> List[ProductEntry]:
        try:
            logger.info(f"Fetching price entries for store brand: {store_brand_id}")
            return await self.product_entry_repo.get_by_store_brand(store_brand_id, db)
        except Exception as e:
            logger.error(f"Error fetching price entries for store brand {store_brand_id}: {str(e)}")
            raise

    async def get_entries_by_store_location(self, store_location_id: int, db: AsyncSession) -> List[ProductEntry]:
        try:
            logger.info(f"Fetching price entries for store location: {store_location_id}")
            return await self.product_entry_repo.get_by_store_location(store_location_id, db)
        except Exception as e:
            logger.error(f"Error fetching price entries for store location {store_location_id}: {str(e)}")
            raise 