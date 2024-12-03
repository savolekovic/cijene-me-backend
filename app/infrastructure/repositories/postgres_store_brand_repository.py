from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID
from app.domain.models import StoreBrand
from app.domain.repositories import StoreBrandRepository
from app.infrastructure.database.models import StoreBrandModel

class PostgresStoreBrandRepository(StoreBrandRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, store_brand: StoreBrand) -> StoreBrand:
        db_store_brand = StoreBrandModel(
            id=store_brand.id,
            name=store_brand.name,
            created_at=store_brand.created_at
        )
        self.session.add(db_store_brand)
        await self.session.commit()
        return store_brand

    async def get_by_id(self, store_brand_id: UUID) -> Optional[StoreBrand]:
        query = select(StoreBrandModel).where(StoreBrandModel.id == store_brand_id)
        result = await self.session.execute(query)
        db_store_brand = result.scalar_one_or_none()
        
        if db_store_brand:
            return StoreBrand(
                id=db_store_brand.id,
                name=db_store_brand.name,
                created_at=db_store_brand.created_at
            )
        return None

    async def get_all(self) -> List[StoreBrand]:
        query = select(StoreBrandModel)
        result = await self.session.execute(query)
        db_store_brands = result.scalars().all()
        
        return [
            StoreBrand(
                id=db_store_brand.id,
                name=db_store_brand.name,
                created_at=db_store_brand.created_at
            )
            for db_store_brand in db_store_brands
        ]

    async def update(self, store_brand_id: UUID, store_brand: StoreBrand) -> Optional[StoreBrand]:
        query = select(StoreBrandModel).where(StoreBrandModel.id == store_brand_id)
        result = await self.session.execute(query)
        db_store_brand = result.scalar_one_or_none()
        
        if db_store_brand:
            db_store_brand.name = store_brand.name
            await self.session.commit()
            return store_brand
        return None

    async def delete(self, store_brand_id: UUID) -> bool:
        query = select(StoreBrandModel).where(StoreBrandModel.id == store_brand_id)
        result = await self.session.execute(query)
        db_store_brand = result.scalar_one_or_none()
        
        if db_store_brand:
            await self.session.delete(db_store_brand)
            await self.session.commit()
            return True
        return False 