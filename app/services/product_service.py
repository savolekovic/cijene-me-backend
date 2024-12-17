from app.domain.repositories.product.product_repo import ProductRepository
from app.domain.repositories.product.category_repo import CategoryRepository
from app.services.cache_service import CacheManager
from app.domain.models.product import Product, ProductWithCategory
from app.infrastructure.logging.logger import get_logger
from app.core.exceptions import NotFoundError, ValidationError
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.responses.product import ProductWithCategoryResponse

logger = get_logger(__name__)

class ProductService:
    def __init__(self, product_repo: ProductRepository, category_repo: CategoryRepository, cache_manager: CacheManager):
        self.product_repo = product_repo
        self.category_repo = category_repo
        self.cache_manager = cache_manager

    async def create_product(self, name: str, image_url: str, category_id: int, db: AsyncSession) -> Product:
        try:
            logger.info(f"Creating new product: {name} in category {category_id}")
            
            # Check if product with same name exists
            existing_product = await self.product_repo.get_by_name(name, db)
            if existing_product:
                logger.error(f"Product with name {name} already exists")
                raise ValidationError(f"Product with name '{name}' already exists")
            
            # Check if category exists
            category = await self.category_repo.get(category_id, db)
            if not category:
                logger.error(f"Category {category_id} not found")
                raise NotFoundError("Category", category_id)
            
            product = await self.product_repo.create(name, image_url, category_id, db)
            logger.info(f"Created product with id: {product.id}")
            await self.cache_manager.clear_product_related_caches()
            return product
        except Exception as e:
            logger.error(f"Error creating product: {str(e)}")
            raise

    async def get_all_products(self, db: AsyncSession) -> List[ProductWithCategoryResponse]:
        try:
            logger.info("Fetching all products with categories")
            return await self.product_repo.get_all(db)
        except Exception as e:
            logger.error(f"Error fetching products with categories: {str(e)}")
            raise

    async def get_product(self, product_id: int, db: AsyncSession) -> ProductWithCategoryResponse:
        try:
            logger.info(f"Fetching product with id: {product_id}")
            product = await self.product_repo.get(product_id, db)
            if not product:
                logger.warning(f"Product not found: {product_id}")
                raise NotFoundError("Product", product_id)
            return product
        except Exception as e:
            logger.error(f"Error fetching product {product_id}: {str(e)}")
            raise

    async def update_product(self, product_id: int, name: str, image_url: str, category_id: int, db: AsyncSession) -> Product:
        try:
            logger.info(f"Updating product {product_id} with name: {name}")
            
            # Check if category exists
            category = await self.category_repo.get(category_id, db)
            if not category:
                logger.error(f"Category {category_id} not found")
                raise NotFoundError("Category", category_id)
            
            # Check if another product with same name exists (excluding current product)
            existing_product = await self.product_repo.get_by_name(name, db)
            if existing_product and existing_product.id != product_id:
                logger.error(f"Another product with name {name} already exists")
                raise ValidationError(f"Product with name '{name}' already exists")
            
            product = Product(
                id=product_id,
                name=name,
                image_url=image_url,
                category_id=category_id
            )
            updated_product = await self.product_repo.update(product_id, product, db)
            if not updated_product:
                logger.warning(f"Product not found for update: {product_id}")
                raise NotFoundError("Product", product_id)
            logger.info(f"Successfully updated product {product_id}")
            await self.cache_manager.clear_product_related_caches()
            return updated_product
        except Exception as e:
            logger.error(f"Error updating product {product_id}: {str(e)}")
            raise

    async def delete_product(self, product_id: int, db: AsyncSession) -> bool:
        try:
            logger.info(f"Attempting to delete product {product_id}")
            success = await self.product_repo.delete(product_id, db)
            if not success:
                logger.warning(f"Product not found for deletion: {product_id}")
                raise NotFoundError("Product", product_id)
            logger.info(f"Successfully deleted product {product_id}")
            await self.cache_manager.clear_product_related_caches()
            return True
        except Exception as e:
            logger.error(f"Error deleting product {product_id}: {str(e)}")
            raise