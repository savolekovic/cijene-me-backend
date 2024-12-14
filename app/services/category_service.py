from app.domain.repositories.product.category_repo import CategoryRepository
from app.services.cache_service import CacheManager
from app.domain.models.product import Category
from app.infrastructure.logging.logger import get_logger
from app.core.exceptions import NotFoundError
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger(__name__)

class CategoryService:
    def __init__(self, category_repo: CategoryRepository, cache_manager: CacheManager):
        self.category_repo = category_repo
        self.cache_manager = cache_manager

    async def create_category(self, name: str, db: AsyncSession) -> Category:
        try:
            logger.info(f"Creating new category: {name}")
            category = await self.category_repo.create(name, db)
            logger.info(f"Created category with id: {category.id}")
            await self.cache_manager.clear_product_related_caches()
            return category
        except Exception as e:
            logger.error(f"Error creating category: {str(e)}")
            raise

    async def get_all_categories(self, db: AsyncSession) -> List[Category]:
        try:
            logger.info("Fetching all categories")
            return await self.category_repo.get_all(db)
        except Exception as e:
            logger.error(f"Error fetching categories: {str(e)}")
            raise

    async def get_category(self, category_id: int, db: AsyncSession) -> Category:
        try:
            logger.info(f"Fetching category with id: {category_id}")
            category = await self.category_repo.get(category_id, db)
            if not category:
                logger.warning(f"Category not found: {category_id}")
                raise NotFoundError("Category", category_id)
            return category
        except Exception as e:
            logger.error(f"Error fetching category {category_id}: {str(e)}")
            raise

    async def delete_category(self, category_id: int, db: AsyncSession) -> bool:
        try:
            logger.info(f"Attempting to delete category {category_id}")
            success = await self.category_repo.delete(category_id, db)
            if not success:
                logger.warning(f"Category not found: {category_id}")
                raise NotFoundError("Category", category_id)
            logger.info(f"Successfully deleted category {category_id}")
            await self.cache_manager.clear_product_related_caches()
            return True
        except Exception as e:
            logger.error(f"Error deleting category {category_id}: {str(e)}")
            raise

    async def update_category(self, category_id: int, name: str, db: AsyncSession) -> Category:
        try:
            logger.info(f"Updating category {category_id} with name: {name}")
            category = Category(id=category_id, name=name)
            updated_category = await self.category_repo.update(category_id, category, db)
            if not updated_category:
                logger.warning(f"Category not found: {category_id}")
                raise NotFoundError("Category", category_id)
            logger.info(f"Successfully updated category {category_id}")
            await self.cache_manager.clear_product_related_caches()
            return updated_category
        except Exception as e:
            logger.error(f"Error updating category {category_id}: {str(e)}")
            raise 