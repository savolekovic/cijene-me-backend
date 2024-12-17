from app.domain.repositories.store.store_location_repo import StoreLocationRepository
from app.services.cache_service import CacheManager
from app.domain.models.store import StoreLocation
from app.infrastructure.logging.logger import get_logger
from app.core.exceptions import NotFoundError
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger(__name__)

class StoreLocationService:
    def __init__(self, store_location_repo: StoreLocationRepository, cache_manager: CacheManager):
        self.store_location_repo = store_location_repo
        self.cache_manager = cache_manager

    async def create_location(self, store_brand_id: int, address: str, db: AsyncSession) -> StoreLocation:
        try:
            logger.info(f"Creating new store location for brand {store_brand_id}")
            location = await self.store_location_repo.create(store_brand_id, address, db)
            logger.info(f"Created store location with id: {location.id}")
            await self.cache_manager.clear_store_related_caches()
            return location
        except Exception as e:
            logger.error(f"Error creating store location: {str(e)}")
            raise

    async def get_all_locations(self, db: AsyncSession) -> List[StoreLocation]:
        try:
            logger.info("Fetching all store locations")
            return await self.store_location_repo.get_all(db)
        except Exception as e:
            logger.error(f"Error fetching store locations: {str(e)}")
            raise

    async def get_location(self, location_id: int, db: AsyncSession) -> StoreLocation:
        try:
            logger.info(f"Fetching store location with id: {location_id}")
            location = await self.store_location_repo.get(location_id, db)
            if not location:
                logger.warning(f"Store location not found: {location_id}")
                raise NotFoundError("Store location", location_id)
            return location
        except Exception as e:
            logger.error(f"Error fetching store location {location_id}: {str(e)}")
            raise

    async def get_store_locations_by_brand(self, store_brand_id: int, db: AsyncSession) -> List[StoreLocation]:
        """Get all store locations for a specific store brand"""
        try:
            logger.info(f"Fetching store locations for brand: {store_brand_id}")
            locations = await self.store_location_repo.get_by_store_brand(store_brand_id, db)
            logger.info(f"Found {len(locations)} locations for brand {store_brand_id}")
            return locations
        except Exception as e:
            logger.error(f"Error fetching locations for brand {store_brand_id}: {str(e)}")
            raise

    async def update_location(self, location_id: int, store_brand_id: int, address: str, db: AsyncSession) -> StoreLocation:
        try:
            logger.info(f"Updating store location {location_id}")
            location = StoreLocation(id=location_id, store_brand_id=store_brand_id, address=address)
            updated_location = await self.store_location_repo.update(location_id, location, db)
            if not updated_location:
                logger.warning(f"Store location not found: {location_id}")
                raise NotFoundError("Store location", location_id)
            logger.info(f"Successfully updated store location {location_id}")
            await self.cache_manager.clear_store_related_caches()
            return updated_location
        except Exception as e:
            logger.error(f"Error updating store location {location_id}: {str(e)}")
            raise

    async def delete_location(self, location_id: int, db: AsyncSession) -> bool:
        try:
            logger.info(f"Attempting to delete store location {location_id}")
            success = await self.store_location_repo.delete(location_id, db)
            if not success:
                logger.warning(f"Store location not found: {location_id}")
                raise NotFoundError("Store location", location_id)
            logger.info(f"Successfully deleted store location {location_id}")
            await self.cache_manager.clear_store_related_caches()
            return True
        except Exception as e:
            logger.error(f"Error deleting store location {location_id}: {str(e)}")
            raise 