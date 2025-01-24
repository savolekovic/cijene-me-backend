from app.api.responses.store import PaginatedStoreBrandResponse, SimpleStoreBrandResponse
from app.domain.repositories.store.store_brand_repo import StoreBrandRepository
from app.services.cache_service import CacheManager
from app.domain.models.store.store_brand import StoreBrand
from app.infrastructure.logging.logger import get_logger
from app.core.exceptions import NotFoundError, ValidationError
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger(__name__)

class StoreBrandService:
    def __init__(self, store_brand_repo: StoreBrandRepository, cache_manager: CacheManager):
        self.store_brand_repo = store_brand_repo
        self.cache_manager = cache_manager

    async def create_store_brand(self, name: str, db: AsyncSession) -> StoreBrand:
        try:
            logger.info(f"Creating new store brand: {name}")
            store_brand = await self.store_brand_repo.create(name, db)
            logger.info(f"Created store brand with id: {store_brand.id}")
            await self.cache_manager.clear_store_related_caches()
            return store_brand
        except Exception as e:
            logger.error(f"Error creating store brand: {str(e)}")
            raise

    async def get_store_brand(self, store_brand_id: int, db: AsyncSession) -> StoreBrand:
        try:
            logger.info(f"Fetching store brand with id: {store_brand_id}")
            store_brand = await self.store_brand_repo.get(store_brand_id, db)
            if not store_brand:
                logger.warning(f"Store brand not found: {store_brand_id}")
                raise NotFoundError("StoreBrand", store_brand_id)
            return store_brand
        except Exception as e:
            logger.error(f"Error fetching store brand {store_brand_id}: {str(e)}")
            raise

    async def get_all_store_brands(self, db: AsyncSession, page: int = 1, per_page: int = 10, search: str = None) -> PaginatedStoreBrandResponse:
        try:
            logger.info(f"Fetching store brands with pagination (page={page}, per_page={per_page}) and search='{search}'")
            return await self.store_brand_repo.get_all(db, page=page, per_page=per_page, search=search)
        except Exception as e:
            logger.error(f"Error fetching store brands: {str(e)}")
            raise

    async def update_store_brand(self, store_brand_id: int, name: str, db: AsyncSession) -> StoreBrand:
        try:
            logger.info(f"Updating store brand {store_brand_id} with name: {name}")
            store_brand = StoreBrand(id=store_brand_id, name=name)
            updated_brand = await self.store_brand_repo.update(store_brand_id, store_brand, db)
            if not updated_brand:
                logger.warning(f"Store brand not found: {store_brand_id}")
                raise NotFoundError("StoreBrand", store_brand_id)
            logger.info(f"Successfully updated store brand {store_brand_id}")
            await self.cache_manager.clear_store_related_caches()
            return updated_brand
        except Exception as e:
            logger.error(f"Error updating store brand {store_brand_id}: {str(e)}")
            raise

    async def delete_store_brand(self, store_brand_id: int, db: AsyncSession) -> bool:
        try:
            logger.info(f"Attempting to delete store brand {store_brand_id}")
            
            # First check if store brand exists
            store_brand = await self.store_brand_repo.get(store_brand_id, db)
            if not store_brand:
                logger.warning(f"Store brand not found: {store_brand_id}")
                raise NotFoundError("StoreBrand", store_brand_id)
            
            # Check if there are any locations for this brand
            locations = await self.store_brand_repo.get_locations_for_brand(store_brand_id, db)
            if locations:
                logger.error(f"Cannot delete store brand {store_brand_id} because it has {len(locations)} locations")
                raise ValidationError(f"Cannot delete store brand because it has {len(locations)} locations. Please delete these locations first.")
            
            success = await self.store_brand_repo.delete(store_brand_id, db)
            logger.info(f"Successfully deleted store brand {store_brand_id}")
            await self.cache_manager.clear_store_related_caches()
            return True
        except Exception as e:
            logger.error(f"Error deleting store brand {store_brand_id}: {str(e)}")
            raise

    async def get_all_store_brands_simple(self, db: AsyncSession, search: str = None) -> List[SimpleStoreBrandResponse]:
        try:
            logger.info(f"Fetching simplified store brands list with search='{search}'")
            return await self.store_brand_repo.get_all_simple(db, search=search)
        except Exception as e:
            logger.error(f"Error getting simplified store brands list: {str(e)}")
            raise 