from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from app.api.responses.category import CategoryResponse
from app.domain.models.product.product import Product
from app.domain.repositories.product.product_repo import ProductRepository
from app.infrastructure.database.models.product import ProductModel
from sqlalchemy import asc
from app.core.exceptions import DatabaseError
from app.infrastructure.database.models.product.category import CategoryModel
from app.api.responses.product import PaginatedProductResponse, ProductWithCategoryResponse, SimpleProductResponse
import logging
from sqlalchemy import func

from app.infrastructure.database.models.product.product_entry import ProductEntryModel

logger = logging.getLogger(__name__)

class PostgresProductRepository(ProductRepository):
    def __init__(self, session: AsyncSession = None):
        self.session = session

    async def get_all(self, db: AsyncSession, page: int = 1, per_page: int = 10, search: str = None) -> PaginatedProductResponse:
        try:
            # Base query for data
            query = (
                select(
                    ProductModel,
                    CategoryModel
                )
                .join(CategoryModel)
            )
            
            # Base query for count
            count_query = select(ProductModel)
            
            # Add search filter if search query is provided
            if search:
                search_pattern = f"%{search}%"
                search_filter = (
                    ProductModel.name.ilike(search_pattern) |
                    ProductModel.barcode.ilike(search_pattern)
                )
                query = query.where(search_filter)
                count_query = count_query.where(search_filter)
            
            # Get total count
            count_result = await db.execute(select(func.count()).select_from(count_query.subquery()))
            total_count = count_result.scalar()
            
            # Add ordering and pagination to the main query
            query = query.order_by(asc(ProductModel.name))
            offset = (page - 1) * per_page
            query = query.offset(offset).limit(per_page)
            
            # Get paginated data
            result = await db.execute(query)
            products = result.all()
            
            # Convert to response model
            product_list = [
                ProductWithCategoryResponse(
                    id=product[0].id,
                    name=product[0].name,
                    barcode=product[0].barcode,
                    image_url=product[0].image_url,
                    created_at=product[0].created_at,
                    category=CategoryResponse(
                        id=product[1].id,
                        name=product[1].name,
                        created_at=product[1].created_at
                    )
                )
                for product in products
            ]
            
            return PaginatedProductResponse(
                total_count=total_count,
                data=product_list
            )
        except Exception as e:
            logger.error(f"Error getting all products: {str(e)}")
            raise DatabaseError(f"Failed to get all products: {str(e)}")

    async def create(self, name: str, barcode: str, image_url: str, category_id: int, db: AsyncSession) -> Product:
        try:
            db_product = ProductModel(
                name=name,
                barcode=barcode,
                image_url=image_url,
                category_id=category_id
            )
            db.add(db_product)
            await db.flush()
            await db.commit()
            return Product(
                id=db_product.id,
                name=db_product.name,
                barcode=db_product.barcode,
                image_url=db_product.image_url,
                category_id=db_product.category_id,
                created_at=db_product.created_at
            )
        except Exception as e:
            logger.error(f"Error creating product: {str(e)}")
            await db.rollback()
            raise DatabaseError(f"Failed to create product: {str(e)}")

    async def get(self, product_id: int, db: AsyncSession) -> Optional[ProductWithCategoryResponse]:
        try:
            query = (
                select(
                    ProductModel,
                    CategoryModel
                )
                .join(CategoryModel)
                .where(ProductModel.id == product_id)
            )
            result = await db.execute(query)
            product = result.first()
            
            if product:
                return ProductWithCategoryResponse(
                    id=product[0].id,
                    name=product[0].name,
                    barcode=product[0].barcode,
                    image_url=product[0].image_url,
                    created_at=product[0].created_at,
                    category=CategoryResponse(
                        id=product[1].id,
                        name=product[1].name,
                        created_at=product[1].created_at
                    )
                )
            return None
        except Exception as e:
            logger.error(f"Error getting product {product_id}: {str(e)}")
            raise DatabaseError(f"Failed to get product: {str(e)}")

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
                db_product.barcode = product.barcode
                await db.flush()
                await db.commit()
                return Product(
                    id=db_product.id,
                    name=db_product.name,
                    barcode=db_product.barcode,
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
            logger.warning(f"Product not found for deletion: {product_id}")
            return False
        except Exception as e:
            logger.error(f"Error deleting product {product_id}: {str(e)}")
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
                    barcode=p.barcode,
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
                    barcode=product.barcode,
                    image_url=product.image_url,
                    category_id=product.category_id,
                    created_at=product.created_at
                )
            return None
        except Exception as e:
            logger.error(f"Error getting product by name: {str(e)}")
            raise DatabaseError(f"Failed to get product by name: {str(e)}") 
        
    async def get_by_barcode(self, barcode: str, db: AsyncSession) -> Optional[Product]:
        try:
            result = await db.execute(
                select(ProductModel).where(ProductModel.barcode == barcode)
            )
            product = result.scalar_one_or_none()
            if product:
                return Product(
                    id=product.id,
                    name=product.name,
                    barcode=product.barcode,
                    image_url=product.image_url,
                    category_id=product.category_id,
                    created_at=product.created_at
                )
            return None
        except Exception as e:
            logger.error(f"Error getting product by barcode: {str(e)}")
            raise DatabaseError(f"Failed to get product by barcode: {str(e)}")

    async def get_product_entries(self, product_id: int, db: AsyncSession) -> List[ProductEntryModel]:
        try:
            result = await db.execute(
                select(ProductEntryModel).where(ProductEntryModel.product_id == product_id)
            )
            entries = result.scalars().all()
            if not entries:
                logger.warning(f"No entries found for product {product_id}")
            return entries
        except Exception as e:
            logger.error(f"Error getting entries for product {product_id}: {str(e)}")
            raise DatabaseError(f"Failed to get product entries: {str(e)}")

    async def get_all_simple(self, db: AsyncSession, search: str = None) -> List[SimpleProductResponse]:
        try:
            # Base query for data
            query = select(ProductModel)
            
            # Add search filter if search query is provided
            if search:
                search_pattern = f"%{search}%"
                search_filter = ProductModel.name.ilike(search_pattern)
                query = query.where(search_filter)
            
            # Add ordering
            query = query.order_by(asc(ProductModel.name))
            
            # Get data
            result = await db.execute(query)
            products = result.scalars().all()
            
            # Convert to response model
            return [
                SimpleProductResponse(
                    id=product.id,
                    name=product.name
                )
                for product in products
            ]
        except Exception as e:
            logger.error(f"Error getting simplified products list: {str(e)}")
            raise DatabaseError(f"Failed to get simplified products list: {str(e)}") 