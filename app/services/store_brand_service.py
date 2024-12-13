from app.domain.repositories.store.store_brand_repo import StoreBrandRepository
from app.services.cache_service import CacheManager
from app.domain.models.store import StoreBrand
from app.infrastructure.logging.logger import get_logger
from app.core.exceptions import NotFoundError
from typing import List

logger = get_logger(__name__)

class StoreBrandService:
    def __init__(self, store_brand_repo: StoreBrandRepository, cache_manager: CacheManager):
        self.store_brand_repo = store_brand_repo
        self.cache_manager = cache_manager

    async def create_store_brand(self, name: str) -> StoreBrand:
        try:
            logger.info(f"Creating new store brand: {name}")
            store_brand = await self.store_brand_repo.create(name)
            logger.info(f"Created store brand with id: {store_brand.id}")
            await self.cache_manager.clear_store_related_caches()
            return store_brand
        except Exception as e:
            logger.error(f"Error creating store brand: {str(e)}")
            raise

    async def get_all_store_brands(self) -> List[StoreBrand]:
        try:
            logger.info("Fetching all store brands")
            return await self.store_brand_repo.get_all()
        except Exception as e:
            logger.error(f"Error fetching store brands: {str(e)}")
            raise

    async def get_store_brand(self, store_brand_id: int) -> StoreBrand:
        try:
            logger.info(f"Fetching store brand with id: {store_brand_id}")
            store_brand = await self.store_brand_repo.get(store_brand_id)
            if not store_brand:
                logger.warning(f"Store brand not found: {store_brand_id}")
                raise NotFoundError("Store brand", store_brand_id)
            return store_brand
        except Exception as e:
            logger.error(f"Error fetching store brand {store_brand_id}: {str(e)}")
            raise

    async def update_store_brand(self, store_brand_id: int, name: str) -> StoreBrand:
        try:
            logger.info(f"Updating store brand {store_brand_id} with name: {name}")
            store_brand = StoreBrand(id=store_brand_id, name=name)
            updated_brand = await self.store_brand_repo.update(store_brand_id, store_brand)
            if not updated_brand:
                logger.warning(f"Store brand not found: {store_brand_id}")
                raise NotFoundError("Store brand", store_brand_id)
            logger.info(f"Successfully updated store brand {store_brand_id}")
            await self.cache_manager.clear_store_related_caches()
            return updated_brand
        except Exception as e:
            logger.error(f"Error updating store brand {store_brand_id}: {str(e)}")
            raise

    async def delete_store_brand(self, store_brand_id: int) -> bool:
        try:
            logger.info(f"Attempting to delete store brand {store_brand_id}")
            success = await self.store_brand_repo.delete(store_brand_id)
            if not success:
                logger.warning(f"Store brand not found: {store_brand_id}")
                raise NotFoundError("Store brand", store_brand_id)
            logger.info(f"Successfully deleted store brand {store_brand_id}")
            await self.cache_manager.clear_store_related_caches()
            return True
        except Exception as e:
            logger.error(f"Error deleting store brand {store_brand_id}: {str(e)}")
            raise 