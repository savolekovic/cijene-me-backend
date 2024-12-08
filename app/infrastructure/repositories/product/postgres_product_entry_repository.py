from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, asc
from typing import List, Optional
from decimal import Decimal
from app.domain.models.product.product_entry import ProductEntry
from app.domain.repositories.product.product_entry_repo import ProductEntryRepository
from app.infrastructure.database.models.product import ProductEntryModel

class PostgresProductEntryRepository(ProductEntryRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self, 
        product_id: int, 
        store_brand_id: int,
        store_location_id: int,
        price: Decimal
    ) -> ProductEntry:
        db_entry = ProductEntryModel(
            product_id=product_id,
            store_brand_id=store_brand_id,
            store_location_id=store_location_id,
            price=price
        )
        self.session.add(db_entry)
        await self.session.commit()
        await self.session.refresh(db_entry)

        return ProductEntry(
            id=db_entry.id,
            product_id=db_entry.product_id,
            store_brand_id=db_entry.store_brand_id,
            store_location_id=db_entry.store_location_id,
            price=db_entry.price,
            created_at=db_entry.created_at
        )

    async def get_all(self) -> List[ProductEntry]:
        query = select(ProductEntryModel).order_by(asc(ProductEntryModel.created_at))
        result = await self.session.execute(query)
        db_entries = result.scalars().all()
        
        return [
            ProductEntry(
                id=entry.id,
                product_id=entry.product_id,
                store_brand_id=entry.store_brand_id,
                store_location_id=entry.store_location_id,
                price=entry.price,
                created_at=entry.created_at
            )
            for entry in db_entries
        ]

    async def get(self, entry_id: int) -> Optional[ProductEntry]:
        query = select(ProductEntryModel).where(ProductEntryModel.id == entry_id)
        result = await self.session.execute(query)
        db_entry = result.scalar_one_or_none()
        
        if db_entry:
            return ProductEntry(
                id=db_entry.id,
                product_id=db_entry.product_id,
                store_brand_id=db_entry.store_brand_id,
                store_location_id=db_entry.store_location_id,
                price=db_entry.price,
                created_at=db_entry.created_at
            )
        return None

    async def get_by_product(self, product_id: int) -> List[ProductEntry]:
        query = select(ProductEntryModel).where(
            ProductEntryModel.product_id == product_id
        ).order_by(asc(ProductEntryModel.created_at))
        result = await self.session.execute(query)
        db_entries = result.scalars().all()
        
        return [
            ProductEntry(
                id=entry.id,
                product_id=entry.product_id,
                store_brand_id=entry.store_brand_id,
                store_location_id=entry.store_location_id,
                price=entry.price,
                created_at=entry.created_at
            )
            for entry in db_entries
        ]

    async def get_by_store_brand(self, store_brand_id: int) -> List[ProductEntry]:
        query = select(ProductEntryModel).where(
            ProductEntryModel.store_brand_id == store_brand_id
        ).order_by(asc(ProductEntryModel.created_at))
        result = await self.session.execute(query)
        db_entries = result.scalars().all()
        
        return [
            ProductEntry(
                id=entry.id,
                product_id=entry.product_id,
                store_brand_id=entry.store_brand_id,
                store_location_id=entry.store_location_id,
                price=entry.price,
                created_at=entry.created_at
            )
            for entry in db_entries
        ]

    async def get_by_store_location(self, store_location_id: int) -> List[ProductEntry]:
        query = select(ProductEntryModel).where(
            ProductEntryModel.store_location_id == store_location_id
        ).order_by(asc(ProductEntryModel.created_at))
        result = await self.session.execute(query)
        db_entries = result.scalars().all()
        
        return [
            ProductEntry(
                id=entry.id,
                product_id=entry.product_id,
                store_brand_id=entry.store_brand_id,
                store_location_id=entry.store_location_id,
                price=entry.price,
                created_at=entry.created_at
            )
            for entry in db_entries
        ] 