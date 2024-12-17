from app.api.responses.product_entry import ProductEntryWithDetails
from app.domain.repositories.product.product_entry_repo import ProductEntryRepository
from app.domain.repositories.store.store_location_repo import StoreLocationRepository
from app.services.cache_service import CacheManager
from app.domain.models.product import ProductEntry
from app.infrastructure.logging.logger import get_logger
from app.core.exceptions import NotFoundError
from typing import List
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger(__name__)

class ProductEntryService:
    def __init__(
        self, 
        product_entry_repo: ProductEntryRepository,
        store_location_repo: StoreLocationRepository,
        cache_manager: CacheManager
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
    ) -> ProductEntry:
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

    async def get_all_entries(self, db: AsyncSession) -> List[ProductEntryWithDetails]:
        try:
            logger.info("Fetching all product entries with details")
            return await self.product_entry_repo.get_all(db)
        except Exception as e:
            logger.error(f"Error fetching product entries with details: {str(e)}")
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
