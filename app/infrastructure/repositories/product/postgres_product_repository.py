from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from app.api.responses.category import CategoryResponse
from app.domain.models.product.product import Product
from app.domain.repositories.product.product_repo import ProductRepository
from app.infrastructure.database.models.product import ProductModel
from sqlalchemy import asc, desc
from app.core.exceptions import DatabaseError
from app.infrastructure.database.models.product.category import CategoryModel
from app.api.responses.product import PaginatedProductResponse, ProductWithCategoryResponse, SimpleProductResponse
import logging
from sqlalchemy import func
from sqlalchemy.orm import joinedload

from app.infrastructure.database.models.product.product_entry import ProductEntryModel

logger = logging.getLogger(__name__)

class PostgresProductRepository(ProductRepository):
    def __init__(self, session: AsyncSession = None):
        self.session = session

    async def get_all(
        self, 
        db: AsyncSession, 
        page: int = 1, 
        per_page: int = 10, 
        search: str = None,
        category_id: int = None,
        has_entries: bool = None,
        min_price: float = None,
        max_price: float = None,
        barcode: str = None,
        order_by: str = "name", 
        order_direction: str = "asc"
    ) -> PaginatedProductResponse:
        try:
            # Base query for data
            query = (
                select(ProductModel, CategoryModel)
                .outerjoin(CategoryModel)
            )
            
            # Base query for count
            count_query = select(ProductModel)
            
            # Add search filter if search query is provided
            if search:
                search_pattern = f"%{search}%"
                search_filter = ProductModel.name.ilike(search_pattern)
                query = query.where(search_filter)
                count_query = count_query.where(search_filter)

            # Add category filter if provided
            if category_id is not None:
                category_filter = ProductModel.category_id == category_id
                query = query.where(category_filter)
                count_query = count_query.where(category_filter)

            # Add barcode filter if provided
            if barcode:
                barcode_filter = ProductModel.barcode == barcode
                query = query.where(barcode_filter)
                count_query = count_query.where(barcode_filter)

            # Add price range filters if provided
            if min_price is not None or max_price is not None or has_entries is not None:
                # Subquery to get latest price for each product
                latest_prices = (
                    select(
                        ProductEntryModel.product_id,
                        func.max(ProductEntryModel.created_at).label('latest_date'),
                        ProductEntryModel.price.label('current_price')
                    )
                    .group_by(ProductEntryModel.product_id, ProductEntryModel.price)
                    .alias('latest_prices')
                )

                query = query.outerjoin(
                    latest_prices,
                    ProductModel.id == latest_prices.c.product_id
                )
                count_query = count_query.outerjoin(
                    latest_prices,
                    ProductModel.id == latest_prices.c.product_id
                )

                if has_entries is not None:
                    if has_entries:
                        query = query.where(latest_prices.c.product_id.isnot(None))
                        count_query = count_query.where(latest_prices.c.product_id.isnot(None))
                    else:
                        query = query.where(latest_prices.c.product_id.is_(None))
                        count_query = count_query.where(latest_prices.c.product_id.is_(None))

                if min_price is not None:
                    query = query.where(latest_prices.c.current_price >= min_price)
                    count_query = count_query.where(latest_prices.c.current_price >= min_price)

                if max_price is not None:
                    query = query.where(latest_prices.c.current_price <= max_price)
                    count_query = count_query.where(latest_prices.c.current_price <= max_price)
            
            # Get total count
            count_result = await db.execute(select(func.count()).select_from(count_query.subquery()))
            total_count = count_result.scalar()
            
            # Add ordering
            order_column = getattr(ProductModel, order_by, ProductModel.name)
            if order_direction.lower() == "desc":
                query = query.order_by(desc(order_column))
            else:
                query = query.order_by(asc(order_column))
            
            # Add pagination
            offset = (page - 1) * per_page
            query = query.offset(offset).limit(per_page)
            
            # Get paginated data
            result = await db.execute(query)
            products = result.all()
            
            # Convert to response model
            product_list = []
            for product, category in products:
                if not category:
                    logger.error(f"Product {product.id} has invalid category data")
                    continue
                
                product_list.append(
                    ProductWithCategoryResponse(
                        id=product.id,
                        name=product.name,
                        barcode=product.barcode,
                        image_url=product.image_url,
                        created_at=product.created_at,
                        category=CategoryResponse(
                            id=category.id,
                            name=category.name,
                            created_at=category.created_at
                        )
                    )
                )
            
            return PaginatedProductResponse(
                total_count=total_count,
                data=product_list
            )
        except Exception as e:
            logger.error(f"Error getting products: {str(e)}")
            raise DatabaseError(f"Failed to get products: {str(e)}")

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