from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import asc, select
from typing import List, Optional
from app.domain.models.store.store_brand import StoreBrand
from app.domain.repositories import StoreBrandRepository
from app.infrastructure.database.models.store import StoreBrandModel
from app.core.exceptions import DatabaseError, NotFoundError

class PostgresStoreBrandRepository(StoreBrandRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, name: str) -> StoreBrand:
        db_store_brand = StoreBrandModel(name=name)
        self.session.add(db_store_brand)
        await self.session.commit()
        await self.session.refresh(db_store_brand)

        return StoreBrand(
            id=db_store_brand.id,
            name=db_store_brand.name,
            created_at=db_store_brand.created_at
        )

    async def get(self, store_brand_id: int) -> Optional[StoreBrand]:
        try:
            query = select(StoreBrandModel).where(StoreBrandModel.id == store_brand_id)
            result = await self.session.execute(query)
            db_store_brand = result.scalar_one_or_none()
            
            if not db_store_brand:
                raise NotFoundError("StoreBrand", store_brand_id)
                
            return StoreBrand(
                id=db_store_brand.id,
                name=db_store_brand.name,
                created_at=db_store_brand.created_at
            )
        except Exception as e:
            if not isinstance(e, NotFoundError):
                raise DatabaseError(str(e))
            raise

    async def get_all(self) -> List[StoreBrand]:
        query = select(StoreBrandModel).order_by(asc(StoreBrandModel.id))
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

    async def update(self, store_brand_id: int, store_brand: StoreBrand) -> Optional[StoreBrand]:
        query = select(StoreBrandModel).where(StoreBrandModel.id == store_brand_id)
        result = await self.session.execute(query)
        db_store_brand = result.scalar_one_or_none()
        
        if db_store_brand:
            db_store_brand.name = store_brand.name
            await self.session.commit()
            await self.session.refresh(db_store_brand)
            return StoreBrand(
                id=db_store_brand.id,
                name=db_store_brand.name,
                created_at=db_store_brand.created_at
            )
        return None

    async def delete(self, store_brand_id: int) -> bool:
        query = select(StoreBrandModel).where(StoreBrandModel.id == store_brand_id)
        result = await self.session.execute(query)
        db_store_brand = result.scalar_one_or_none()
        
        if db_store_brand:
            await self.session.delete(db_store_brand)
            await self.session.commit()
            return True
        return False 