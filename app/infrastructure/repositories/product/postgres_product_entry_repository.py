from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, asc
from typing import List, Optional
from decimal import Decimal
from app.domain.models.product.product_entry import ProductEntry
from app.domain.repositories.product.product_entry_repo import ProductEntryRepository
from app.infrastructure.database.models.product import ProductEntryModel
from app.infrastructure.logging.logger import get_logger

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
    ) -> ProductEntry:
        product_entry_db = ProductEntryModel(
            product_id=product_id,
            store_brand_id=store_brand_id,
            store_location_id=store_location_id,
            price=price
        )
        db.add(product_entry_db)
        await db.flush()
        await db.commit()
        return ProductEntry.model_validate(product_entry_db)

    async def get_all(self, db: AsyncSession) -> List[ProductEntry]:
        result = await db.execute(select(ProductEntryModel))
        product_entries = result.scalars().all()
        return [ProductEntry.model_validate(product_entry) for product_entry in product_entries]

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