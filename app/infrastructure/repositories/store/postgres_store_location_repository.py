from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, asc
from typing import List, Optional
from app.domain.models.store.store_location import StoreLocation
from app.domain.repositories.store.store_location_repo import StoreLocationRepository
from app.infrastructure.database.models.store import StoreBrandModel, StoreLocationModel

class PostgresStoreLocationRepository(StoreLocationRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, store_brand_id: int, address: str) -> StoreLocation:
        # First check if store brand exists
        store_brand_query = select(StoreBrandModel).where(StoreBrandModel.id == store_brand_id)
        store_brand_result = await self.session.execute(store_brand_query)
        store_brand = store_brand_result.scalar_one_or_none()
        
        if not store_brand:
            raise ValueError(f"Store brand not found")

        db_location = StoreLocationModel(store_brand_id=store_brand_id, address=address)
        self.session.add(db_location)
        await self.session.commit()
        await self.session.refresh(db_location)

        return StoreLocation(
            id=db_location.id,
            store_brand_id=db_location.store_brand_id,
            address=db_location.address,
            created_at=db_location.created_at
        )

    async def get(self, location_id: int) -> Optional[StoreLocation]:
        query = select(StoreLocationModel).where(StoreLocationModel.id == location_id)
        result = await self.session.execute(query)
        db_location = result.scalar_one_or_none()
        
        if db_location:
            return StoreLocation(
                id=db_location.id,
                store_brand_id=db_location.store_brand_id,
                address=db_location.address,
                created_at=db_location.created_at
            )
        return None

    async def get_all(self) -> List[StoreLocation]:
        query = select(StoreLocationModel).order_by(asc(StoreLocationModel.id))
        result = await self.session.execute(query)
        db_locations = result.scalars().all()
        
        return [
            StoreLocation(
                id=db_location.id,
                store_brand_id=db_location.store_brand_id,
                address=db_location.address,
                created_at=db_location.created_at
            )
            for db_location in db_locations
        ]

    async def get_by_store_brand(self, store_brand_id: int) -> List[StoreLocation]:
        query = select(StoreLocationModel).where(
            StoreLocationModel.store_brand_id == store_brand_id
        ).order_by(asc(StoreLocationModel.id))
        result = await self.session.execute(query)
        db_locations = result.scalars().all()
        
        return [
            StoreLocation(
                id=db_location.id,
                store_brand_id=db_location.store_brand_id,
                address=db_location.address,
                created_at=db_location.created_at
            )
            for db_location in db_locations
        ]

    async def update(self, location_id: int, store_location: StoreLocation) -> Optional[StoreLocation]:
        query = select(StoreLocationModel).where(StoreLocationModel.id == location_id)
        result = await self.session.execute(query)
        db_location = result.scalar_one_or_none()
        
        if db_location:
            db_location.address = store_location.address
            await self.session.commit()
            await self.session.refresh(db_location)
            return StoreLocation(
                id=db_location.id,
                store_brand_id=db_location.store_brand_id,
                address=db_location.address,
                created_at=db_location.created_at
            )
        return None

    async def delete(self, location_id: int) -> bool:
        query = select(StoreLocationModel).where(StoreLocationModel.id == location_id)
        result = await self.session.execute(query)
        db_location = result.scalar_one_or_none()
        
        if db_location:
            await self.session.delete(db_location)
            await self.session.commit()
            return True
        return False 