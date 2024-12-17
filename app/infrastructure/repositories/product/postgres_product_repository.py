from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from app.domain.models.product.product import Product
from app.domain.repositories.product.product_repo import ProductRepository
from app.infrastructure.database.models.product import ProductModel
from sqlalchemy import asc
from app.core.exceptions import DatabaseError
from app.infrastructure.database.models.product.category import CategoryModel
from app.api.responses.product import CategoryInProduct, ProductWithCategoryResponse
import logging

logger = logging.getLogger(__name__)

class PostgresProductRepository(ProductRepository):
    def __init__(self, session: AsyncSession = None):
        pass

    async def get_all_with_categories(self, db: AsyncSession) -> List[ProductWithCategoryResponse]:
        try:
            query = (
                select(
                    ProductModel,
                    CategoryModel
                )
                .join(CategoryModel)
                .order_by(asc(ProductModel.name))
            )
            
            result = await db.execute(query)
            products = result.all()
            
            return [
                ProductWithCategoryResponse(
                    id=product[0].id,
                    name=product[0].name,
                    image_url=product[0].image_url,
                    created_at=product[0].created_at,
                    category=CategoryInProduct(
                        id=product[1].id,
                        name=product[1].name
                    )
                )
                for product in products
            ]
        except Exception as e:
            logger.error(f"Error getting products with categories: {str(e)}")
            raise DatabaseError(f"Failed to get products: {str(e)}")

    async def create(self, name: str, image_url: str, category_id: int, db: AsyncSession) -> Product:
        try:
            db_product = ProductModel(
                name=name,
                image_url=image_url,
                category_id=category_id
            )
            db.add(db_product)
            await db.flush()
            await db.commit()
            
            return Product(
                id=db_product.id,
                name=db_product.name,
                image_url=db_product.image_url,
                category_id=db_product.category_id,
                created_at=db_product.created_at
            )
        except Exception as e:
            logger.error(f"Error creating product: {str(e)}")
            await db.rollback()
            raise DatabaseError(f"Failed to create product: {str(e)}")

    async def get(self, product_id: int, db: AsyncSession) -> Optional[Product]:
        try:
            result = await db.execute(
                select(ProductModel).where(ProductModel.id == product_id)
            )
            product = result.scalar_one_or_none()
            if product:
                return Product(
                    id=product.id,
                    name=product.name,
                    image_url=product.image_url,
                    category_id=product.category_id,
                    created_at=product.created_at
                )
            return None
        except Exception as e:
            logger.error(f"Error getting product: {str(e)}")
            raise DatabaseError(f"Failed to get product: {str(e)}")

    async def get_all(self, db: AsyncSession) -> List[Product]:
        try:
            result = await db.execute(
                select(ProductModel).order_by(asc(ProductModel.name))
            )
            products = result.scalars().all()
            return [
                Product(
                    id=p.id,
                    name=p.name,
                    image_url=p.image_url,
                    category_id=p.category_id,
                    created_at=p.created_at
                ) for p in products
            ]
        except Exception as e:
            logger.error(f"Error getting all products: {str(e)}")
            raise DatabaseError(f"Failed to get products: {str(e)}")

    async def update(self, product_id: int, product: Product, db: AsyncSession) -> Optional[Product]:
        try:
            result = await db.execute(
                select(ProductModel).where(ProductModel.id == product_id)
            )
            db_product = result.scalar_one_or_none()
            if db_product:
                db_product.name = product.name
                db_product.image_url = product.image_url
                db_product.category_id = product.category_id
                await db.flush()
                await db.commit()
                return Product(
                    id=db_product.id,
                    name=db_product.name,
                    image_url=db_product.image_url,
                    category_id=db_product.category_id,
                    created_at=db_product.created_at
                )
            return None
        except Exception as e:
            logger.error(f"Error updating product: {str(e)}")
            await db.rollback()
            raise DatabaseError(f"Failed to update product: {str(e)}")

    async def delete(self, product_id: int, db: AsyncSession) -> bool:
        try:
            result = await db.execute(
                select(ProductModel).where(ProductModel.id == product_id)
            )
            product = result.scalar_one_or_none()
            if product:
                await db.delete(product)
                await db.flush()
                await db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting product: {str(e)}")
            await db.rollback()
            raise DatabaseError(f"Failed to delete product: {str(e)}")

    async def get_by_category(self, category_id: int, db: AsyncSession) -> List[Product]:
        try:
            result = await db.execute(
                select(ProductModel)
                .where(ProductModel.category_id == category_id)
                .order_by(asc(ProductModel.name))
            )
            products = result.scalars().all()
            return [
                Product(
                    id=p.id,
                    name=p.name,
                    image_url=p.image_url,
                    category_id=p.category_id,
                    created_at=p.created_at
                ) for p in products
            ]
        except Exception as e:
            logger.error(f"Error getting products by category: {str(e)}")
            raise DatabaseError(f"Failed to get products by category: {str(e)}")

    async def get_by_name(self, name: str, db: AsyncSession) -> Optional[Product]:
        try:
            result = await db.execute(
                select(ProductModel).where(ProductModel.name.ilike(name))
            )
            product = result.scalar_one_or_none()
            if product:
                return Product(
                    id=product.id,
                    name=product.name,
                    image_url=product.image_url,
                    category_id=product.category_id,
                    created_at=product.created_at
                )
            return None
        except Exception as e:
            logger.error(f"Error getting product by name: {str(e)}")
            raise DatabaseError(f"Failed to get product by name: {str(e)}") 