from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, asc, desc
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
from app.api.responses.product_entry import ProductEntryWithDetails, ProductInEntry, StoreBrandInEntry, StoreLocationInEntry, ProductWithCategoryResponse
from app.api.responses.product import CategoryInProduct

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
                    barcode=entry[1].barcode
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
        result = await db.execute(
            select(ProductEntryModel).where(ProductEntryModel.id == entry_id)
        )
        product_entry = result.scalar_one_or_none()
        return ProductEntry.model_validate(product_entry) if product_entry else None

    async def get_by_product(self, product_id: int, db: AsyncSession) -> List[ProductEntry]:
        result = await db.execute(
            select(ProductEntryModel).where(ProductEntryModel.product_id == product_id)
        )
        product_entry = result.scalar_one_or_none()
        return ProductEntry.model_validate(product_entry) if product_entry else None

    async def get_by_store_brand(self, store_brand_id: int, db: AsyncSession) -> List[ProductEntry]:
        result = await db.execute(
            select(ProductEntryModel).where(ProductEntryModel.store_brand_id == store_brand_id)
        )
        product_entry = result.scalar_one_or_none()
        return ProductEntry.model_validate(product_entry) if product_entry else None

    async def get_by_store_location(self, store_location_id: int, db: AsyncSession) -> List[ProductEntry]:
        result = await db.execute(
            select(ProductEntryModel).where(ProductEntryModel.store_location_id == store_location_id)
        )
        product_entry = result.scalar_one_or_none()
        return ProductEntry.model_validate(product_entry) if product_entry else None

    async def get_all(self, db: AsyncSession) -> List[ProductEntryWithDetails]:
        try:
            query = (
                select(ProductEntryModel)
                .options(
                    joinedload(ProductEntryModel.product)
                    .joinedload(ProductModel.category),
                    joinedload(ProductEntryModel.store_location)
                    .joinedload(StoreLocationModel.store_brand)
                )
                .order_by(desc(ProductEntryModel.created_at))
            )
            result = await db.execute(query)
            entries = result.unique().scalars().all()
            
            return [
                ProductEntryWithDetails(
                    id=entry.id,
                    price=entry.price,
                    created_at=entry.created_at,
                    product=ProductWithCategoryResponse(
                        id=entry.product.id,
                        name=entry.product.name,
                        barcode=entry.product.barcode,
                        image_url=entry.product.image_url,
                        category=CategoryInProduct(
                            id=entry.product.category.id,
                            name=entry.product.category.name
                        ),
                        created_at=entry.product.created_at
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
                for entry in entries
            ]
        except Exception as e:
            logger.error(f"Error getting all product entries: {str(e)}")
            raise

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