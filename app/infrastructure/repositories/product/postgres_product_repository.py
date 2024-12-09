from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from app.domain.models.product.product import Product, ProductWithCategory
from app.domain.repositories.product.product_repo import ProductRepository
from app.infrastructure.database.models.product import ProductModel
from sqlalchemy import asc
from app.core.exceptions import DatabaseError
import logging

from app.infrastructure.database.models.product.category import CategoryModel

logger = logging.getLogger(__name__)

class PostgresProductRepository(ProductRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def get_all_with_categories(self) -> List[ProductWithCategory]:
        query = select(ProductModel, CategoryModel.name.label('category_name'))\
            .join(CategoryModel)\
            .order_by(asc(ProductModel.name))
        
        result = await self.session.execute(query)
        products_with_categories = result.all()
        
        return [
            ProductWithCategory(
                id=product.id,
                name=product.name,
                image_url=product.image_url,
                category_id=product.category_id,
                category_name=category_name,
                created_at=product.created_at
            )
            for product, category_name in products_with_categories
        ] 

    async def create(self, name: str, image_url: str, category_id: int) -> Product:
        try:
            db_product = ProductModel(
                name=name,
                image_url=image_url,
                category_id=category_id
            )
            self.session.add(db_product)
            await self.session.commit()
            await self.session.refresh(db_product)

            return Product(
                id=db_product.id,
                name=db_product.name,
                image_url=db_product.image_url,
                category_id=db_product.category_id,
                created_at=db_product.created_at
            )
        except Exception as e:
            logger.error(f"Error creating product: {str(e)}")
            raise DatabaseError(f"Failed to create product: {str(e)}")

    async def get(self, product_id: int) -> Optional[Product]:
        try:
            query = select(ProductModel).where(ProductModel.id == product_id)
            result = await self.session.execute(query)
            db_product = result.scalar_one_or_none()
            
            if db_product:
                return Product(
                    id=db_product.id,
                    name=db_product.name,
                    image_url=db_product.image_url,
                    category_id=db_product.category_id,
                    created_at=db_product.created_at
                )
            return None
        except Exception as e:
            logger.error(f"Error getting product: {str(e)}")
            raise DatabaseError(f"Failed to get product: {str(e)}")

    async def get_all(self) -> List[Product]:
        try:
            query = select(ProductModel).order_by(asc(ProductModel.name))
            result = await self.session.execute(query)
            db_products = result.scalars().all()
            
            return [
                Product(
                    id=product.id,
                    name=product.name,
                    image_url=product.image_url,
                    category_id=product.category_id,
                    created_at=product.created_at
                )
                for product in db_products
            ]
        except Exception as e:
            logger.error(f"Error getting all products: {str(e)}")
            raise DatabaseError(f"Failed to get products: {str(e)}") 