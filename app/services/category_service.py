from app.domain.repositories.product.category_repo import CategoryRepository
from app.services.cache_service import CacheManager
from app.domain.models.product import Category
from app.infrastructure.logging.logger import get_logger
from app.core.exceptions import NotFoundError, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.responses.category import PaginatedCategoryResponse, SimpleCategoryResponse
from typing import List

logger = get_logger(__name__)

class CategoryService:
    def __init__(self, category_repo: CategoryRepository, cache_manager: CacheManager):
        self.category_repo = category_repo
        self.cache_manager = cache_manager

    async def create_category(self, name: str, db: AsyncSession) -> Category:
        try:
            logger.info(f"Creating new category: {name}")
            
            # Check if category with same name exists
            existing_category = await self.category_repo.get_by_name(name, db)
            if existing_category:
                logger.error(f"Category with name {name} already exists")
                raise ValidationError(f"Category with name '{name}' already exists")
            
            category = await self.category_repo.create(name, db)
            logger.info(f"Created category with id: {category.id}")
            await self.cache_manager.clear_product_related_caches()
            return category
        except Exception as e:
            logger.error(f"Error creating category: {str(e)}")
            raise

    async def get_all_categories(self, db: AsyncSession, page: int = 1, per_page: int = 10, search: str = None, order_by: str = "name", order_direction: str = "asc") -> PaginatedCategoryResponse:
        try:
            logger.info(f"Fetching categories with pagination (page={page}, per_page={per_page}) and search='{search}', order_by={order_by}, order_direction={order_direction}")
            return await self.category_repo.get_all(
                db=db,
                page=page,
                per_page=per_page,
                search=search,
                order_by=order_by,
                order_direction=order_direction
            )
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
            
            # First check if category exists
            category = await self.category_repo.get(category_id, db)
            if not category:
                logger.warning(f"Category not found: {category_id}")
                raise NotFoundError("Category", category_id)
            
            # Check if there are any products in this category
            products = await self.category_repo.get_products_in_category(category_id, db)
            if products:
                logger.error(f"Cannot delete category {category_id} because it contains {len(products)} products")
                raise ValidationError(f"Cannot delete category because it contains {len(products)} products. Please move or delete these products first.")
            
            success = await self.category_repo.delete(category_id, db)
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

    async def get_all_categories_simple(self, db: AsyncSession, search: str = None) -> List[SimpleCategoryResponse]:
        try:
            logger.info(f"Fetching simplified categories list with search='{search}'")
            return await self.category_repo.get_all_simple(db, search=search)
        except Exception as e:
            logger.error(f"Error fetching simplified categories list: {str(e)}")
            raise 