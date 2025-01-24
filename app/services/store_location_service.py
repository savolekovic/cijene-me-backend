from app.api.responses.store import StoreLocationResponse, PaginatedStoreLocationResponse, SimpleStoreLocationResponse
from app.domain.repositories.store.store_location_repo import StoreLocationRepository
from app.services.cache_service import CacheManager
from app.domain.models.store import StoreLocation
from app.infrastructure.logging.logger import get_logger
from app.core.exceptions import DatabaseError, NotFoundError, ConflictError, ValidationError
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger(__name__)

class StoreLocationService:
    def __init__(self, store_location_repo: StoreLocationRepository, cache_manager: CacheManager):
        self.store_location_repo = store_location_repo
        self.cache_manager = cache_manager

    async def create_location(self, store_brand_id: int, address: str, db: AsyncSession) -> StoreLocationResponse:
        try:
            logger.info(f"Creating new store location for brand {store_brand_id}")
            location = await self.store_location_repo.create(store_brand_id, address, db)
            logger.info(f"Created store location with id: {location.id}")
            await self.cache_manager.clear_store_related_caches()
            return location
        except DatabaseError as e:
            if "already exists" in str(e):
                logger.warning(f"Attempted to create duplicate store location: {str(e)}")
                raise ConflictError(f"Store location already exists with this address for the given brand")
            logger.error(f"Database error creating store location: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error creating store location: {str(e)}")
            raise

    async def get_all_store_locations(self, db: AsyncSession, page: int = 1, per_page: int = 10, search: str = None) -> PaginatedStoreLocationResponse:
        try:
            logger.info(f"Fetching store locations with pagination (page={page}, per_page={per_page}) and search='{search}'")
            return await self.store_location_repo.get_all(db, page=page, per_page=per_page, search=search)
        except Exception as e:
            logger.error(f"Error fetching store locations: {str(e)}")
            raise

    async def get_location(self, location_id: int, db: AsyncSession) -> StoreLocationResponse:
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

    async def get_store_locations_by_brand(self, store_brand_id: int, db: AsyncSession) -> List[StoreLocationResponse]:
        try:
            logger.info(f"Fetching store locations for brand: {store_brand_id}")
            locations = await self.store_location_repo.get_by_store_brand(store_brand_id, db)
            logger.info(f"Found {len(locations)} locations for brand {store_brand_id}")
            return locations
        except Exception as e:
            logger.error(f"Error fetching locations for brand {store_brand_id}: {str(e)}")
            raise

    async def update_location(self, location_id: int, store_brand_id: int, address: str, db: AsyncSession) -> StoreLocationResponse:
        try:
            logger.info(f"Updating store location {location_id}")
            location = StoreLocation(
                id=location_id,
                store_brand_id=store_brand_id,
                address=address
            )
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
            
            # First check if location exists
            location = await self.store_location_repo.get(location_id, db)
            if not location:
                logger.warning(f"Store location not found: {location_id}")
                raise NotFoundError("StoreLocation", location_id)
            
            # Check if there are any product entries for this location
            entries = await self.store_location_repo.get_product_entries_for_location(location_id, db)
            if entries:
                logger.error(f"Cannot delete store location {location_id} because it has {len(entries)} product entries")
                raise ValidationError(f"Cannot delete store location because it has {len(entries)} price entries. Please delete these entries first.")
            
            await self.store_location_repo.delete(location_id, db)
            logger.info(f"Successfully deleted store location {location_id}")
            await self.cache_manager.clear_store_related_caches()
            return True
        except Exception as e:
            logger.error(f"Error deleting store location {location_id}: {str(e)}")
            raise

    async def get_all_store_locations_simple(self, db: AsyncSession, search: str = None, store_brand_id: int = None) -> List[SimpleStoreLocationResponse]:
        try:
            logger.info(f"Fetching simplified store locations list with search='{search}', store_brand_id={store_brand_id}")
            return await self.store_location_repo.get_all_simple(db, search=search, store_brand_id=store_brand_id)
        except Exception as e:
            logger.error(f"Error getting simplified store locations list: {str(e)}")
            raise 