from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, or_, and_, asc
from sqlalchemy.orm import joinedload
from typing import List, Optional
from decimal import Decimal
from app.core.exceptions import DatabaseError
from app.domain.models.product.product_entry import ProductEntry
from app.domain.repositories.product.product_entry_repo import ProductEntryRepository
from app.infrastructure.database.models.product import ProductEntryModel
from app.infrastructure.database.models.product.product import ProductModel
from app.infrastructure.database.models.store.store_brand import StoreBrandModel
from app.infrastructure.database.models.store.store_location import StoreLocationModel
from app.infrastructure.logging.logger import get_logger
from app.api.responses.product_entry import (
    ProductEntryWithDetails,
    ProductInEntry,
    StoreBrandInEntry,
    StoreLocationInEntry,
    PaginatedProductEntryResponse
)
from datetime import datetime

logger = get_logger(__name__)

class PostgresProductEntryRepository(ProductEntryRepository):
    def __init__(self, session: AsyncSession = None):
        self.session = session

    async def create(
        self, 
        product_id: int, 
        store_brand_id: int,
        store_location_id: int,
        price: Decimal,
        db: AsyncSession
    ) -> ProductEntryWithDetails:
        try:
            # Create the entry
            product_entry_db = ProductEntryModel(
                product_id=product_id,
                store_brand_id=store_brand_id,
                store_location_id=store_location_id,
                price=price
            )
            db.add(product_entry_db)
            await db.flush()

            # Load related models in a single query
            query = (
                select(
                    ProductEntryModel,
                    ProductModel,
                    StoreLocationModel,
                    StoreBrandModel
                )
                .join(ProductModel, ProductEntryModel.product_id == ProductModel.id)
                .join(StoreLocationModel, ProductEntryModel.store_location_id == StoreLocationModel.id)
                .join(StoreBrandModel, ProductEntryModel.store_brand_id == StoreBrandModel.id)
                .where(ProductEntryModel.id == product_entry_db.id)
            )
            
            result = await db.execute(query)
            entry = result.first()
            await db.commit()
            
            # Convert to response model
            return ProductEntryWithDetails(
                id=entry[0].id,
                price=float(entry[0].price),
                created_at=entry[0].created_at,
                product=ProductInEntry(
                    id=entry[1].id,
                    name=entry[1].name,
                    image_url=entry[1].image_url
                ),
                store_location=StoreLocationInEntry(
                    id=entry[2].id,
                    address=entry[2].address,
                    store_brand=StoreBrandInEntry(
                        id=entry[3].id,
                        name=entry[3].name
                    )
                )
            )
        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating product entry: {str(e)}")
            raise DatabaseError(f"Failed to create product entry: {str(e)}")

    async def get(self, entry_id: int, db: AsyncSession) -> Optional[ProductEntry]:
        try:
            result = await db.execute(
                select(ProductEntryModel).where(ProductEntryModel.id == entry_id)
            )
            product_entry = result.scalar_one_or_none()
            if product_entry:
                return ProductEntry(
                    id=product_entry.id,
                    price=product_entry.price,
                    product_id=product_entry.product_id,
                    store_brand_id=product_entry.store_brand_id,
                    store_location_id=product_entry.store_location_id,
                    created_at=product_entry.created_at
                )
            return None
        except Exception as e:
            logger.error(f"Error getting product entry {entry_id}: {str(e)}")
            raise DatabaseError(f"Failed to get product entry: {str(e)}")

    async def get_by_product_and_store(self, product_id: int, store_location_id: int, db: AsyncSession) -> Optional[ProductEntry]:
        try:
            result = await db.execute(
                select(ProductEntryModel)
                .where(
                    and_(
                        ProductEntryModel.product_id == product_id,
                        ProductEntryModel.store_location_id == store_location_id
                    )
                )
            )
            product_entry = result.scalar_one_or_none()
            if product_entry:
                return ProductEntry(
                    id=product_entry.id,
                    price=product_entry.price,
                    product_id=product_entry.product_id,
                    store_location_id=product_entry.store_location_id,
                    created_at=product_entry.created_at
                )
            return None
        except Exception as e:
            logger.error(f"Error getting product entry by product and store: {str(e)}")
            raise DatabaseError(f"Failed to get product entry by product and store: {str(e)}")

    async def get_by_product(self, product_id: int, db: AsyncSession) -> List[ProductEntry]:
        try:
            result = await db.execute(
                select(ProductEntryModel).where(ProductEntryModel.product_id == product_id)
            )
            entries = result.scalars().all()
            return [
                ProductEntry(
                    id=entry.id,
                    price=entry.price,
                    product_id=entry.product_id,
                    store_brand_id=entry.store_brand_id,
                    store_location_id=entry.store_location_id,
                    created_at=entry.created_at
                ) for entry in entries
            ]
        except Exception as e:
            logger.error(f"Error getting product entry by product: {str(e)}")
            raise DatabaseError(f"Failed to get product entry by product: {str(e)}")

    async def get_by_store_location(self, store_location_id: int, db: AsyncSession) -> Optional[ProductEntry]:
        try:
            result = await db.execute(
                select(ProductEntryModel).where(ProductEntryModel.store_location_id == store_location_id)
            )
            product_entry = result.scalar_one_or_none()
            if product_entry:
                return ProductEntry(
                    id=product_entry.id,
                    price=product_entry.price,
                    product_id=product_entry.product_id,
                    store_location_id=product_entry.store_location_id,
                    created_at=product_entry.created_at
                )
            return None
        except Exception as e:
            logger.error(f"Error getting product entry by store location: {str(e)}")
            raise DatabaseError(f"Failed to get product entry by store location: {str(e)}")

    async def get_by_store_brand(self, store_brand_id: int, db: AsyncSession) -> List[ProductEntry]:
        result = await db.execute(
            select(ProductEntryModel).where(ProductEntryModel.store_brand_id == store_brand_id)
        )
        product_entry = result.scalar_one_or_none()
        if product_entry:
                return ProductEntry(
                    id = product_entry.id,
                    product_id = product_entry.product_id,
                    store_brand_id = product_entry.store_brand_id,
                    store_location_id = product_entry.store_location_id,
                    price = product_entry.price,
                    created_at = product_entry.created_at
                )
        return None

    async def get_all(
        self, 
        db: AsyncSession, 
        page: int = 1, 
        per_page: int = 10, 
        search: str = None,
        product_id: int = None,
        store_brand_id: int = None,
        store_location_id: int = None,
        min_price: float = None,
        max_price: float = None,
        from_date: datetime = None,
        to_date: datetime = None,
        order_by: str = "created_at", 
        order_direction: str = "desc"
    ) -> PaginatedProductEntryResponse:
        try:
            # Base query for data
            query = (
                select(ProductEntryModel)
                .options(
                    joinedload(ProductEntryModel.product),
                    joinedload(ProductEntryModel.store_location)
                    .joinedload(StoreLocationModel.store_brand)
                )
            )
            
            # Base query for count
            count_query = select(ProductEntryModel)
            
            # Add product_id filter if provided
            if product_id is not None:
                product_filter = ProductEntryModel.product_id == product_id
                query = query.where(product_filter)
                count_query = count_query.where(product_filter)
            
            # Add store_brand_id filter if provided
            if store_brand_id is not None:
                store_brand_filter = ProductEntryModel.store_brand_id == store_brand_id
                query = query.where(store_brand_filter)
                count_query = count_query.where(store_brand_filter)
            
            # Add store_location_id filter if provided
            if store_location_id is not None:
                store_location_filter = ProductEntryModel.store_location_id == store_location_id
                query = query.where(store_location_filter)
                count_query = count_query.where(store_location_filter)
            
            # Add price range filters if provided
            if min_price is not None:
                price_min_filter = ProductEntryModel.price >= min_price
                query = query.where(price_min_filter)
                count_query = count_query.where(price_min_filter)
            if max_price is not None:
                price_max_filter = ProductEntryModel.price <= max_price
                query = query.where(price_max_filter)
                count_query = count_query.where(price_max_filter)
            
            # Add date range filters if provided
            if from_date is not None:
                date_from_filter = ProductEntryModel.created_at >= from_date
                query = query.where(date_from_filter)
                count_query = count_query.where(date_from_filter)
            if to_date is not None:
                date_to_filter = ProductEntryModel.created_at <= to_date
                query = query.where(date_to_filter)
                count_query = count_query.where(date_to_filter)
            
            # Add search filter if search query is provided
            if search:
                search_pattern = f"%{search}%"
                # Join the necessary tables for search
                count_query = (
                    count_query
                    .join(ProductModel)
                    .join(StoreLocationModel)
                    .join(StoreBrandModel)
                )
                # Search across product name, store brand name, and store location address
                search_filter = or_(
                    ProductModel.name.ilike(search_pattern),
                    StoreBrandModel.name.ilike(search_pattern),
                    StoreLocationModel.address.ilike(search_pattern)
                )
                query = query.join(ProductEntryModel.product).join(ProductEntryModel.store_location).join(StoreLocationModel.store_brand).where(search_filter)
                count_query = count_query.where(search_filter)
            
            # Get total count
            count_result = await db.execute(select(func.count()).select_from(count_query.subquery()))
            total_count = count_result.scalar()
            
            # Add ordering
            order_column = getattr(ProductEntryModel, order_by, ProductEntryModel.created_at)
            if order_direction.lower() == "desc":
                query = query.order_by(desc(order_column))
            else:
                query = query.order_by(asc(order_column))
            
            # Add pagination
            offset = (page - 1) * per_page
            query = query.offset(offset).limit(per_page)
            
            # Get paginated data
            result = await db.execute(query)
            entries = result.unique().scalars().all()
            
            # Convert to response model
            entry_list = []
            for entry in entries:
                if not entry.product:
                    logger.error(f"Product entry {entry.id} has invalid product data")
                    continue
                
                entry_list.append(
                    ProductEntryWithDetails(
                        id=entry.id,
                        price=float(entry.price),
                        created_at=entry.created_at,
                        product=ProductInEntry(
                            id=entry.product.id,
                            name=entry.product.name,
                            image_url=entry.product.image_url
                        ),
                        store_location=StoreLocationInEntry(
                            id=entry.store_location.id,
                            address=entry.store_location.address,
                            store_brand=StoreBrandInEntry(
                                id=entry.store_location.store_brand.id,
                                name=entry.store_location.store_brand.name
                            )
                        )
                    )
                )
            
            return PaginatedProductEntryResponse(
                total_count=total_count,
                data=entry_list
            )
        except Exception as e:
            logger.error(f"Error getting product entries: {str(e)}")
            raise DatabaseError(f"Failed to get product entries: {str(e)}")

    async def delete(self, entry_id: int, db: AsyncSession) -> bool:
        try:
            result = await db.execute(
                select(ProductEntryModel).where(ProductEntryModel.id == entry_id)
            )
            entry = result.scalar_one_or_none()
            if entry:
                await db.delete(entry)
                await db.flush()
                await db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting product entry: {str(e)}")
            await db.rollback()
            raise DatabaseError(f"Failed to delete product entry: {str(e)}")