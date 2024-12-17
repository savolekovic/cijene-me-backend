from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, asc
from typing import List, Optional
from app.core.exceptions import DatabaseError, NotFoundError
from app.domain.models.store.store_location import StoreLocation
from app.domain.repositories.store.store_location_repo import StoreLocationRepository
from app.infrastructure.database.models.store import StoreBrandModel, StoreLocationModel
from app.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)

class PostgresStoreLocationRepository(StoreLocationRepository):
    def __init__(self, session: AsyncSession = None):
        self.session = session

    async def create(self, store_brand_id: int, address: str, db: AsyncSession) -> StoreLocation:
        store_location_db = StoreLocationModel(store_brand_id=store_brand_id, address=address)
        db.add(store_location_db)
        await db.flush()
        await db.commit()
        return StoreLocation.model_validate(store_location_db)

    async def get(self, location_id: int, db: AsyncSession) -> Optional[StoreLocation]:
        result = await db.execute(
            select(StoreLocationModel).where(StoreLocationModel.id == location_id)
        )
        store_location = result.scalar_one_or_none()
        return StoreLocation.model_validate(store_location) if store_location else None

    async def get_all(self, db: AsyncSession) -> List[StoreLocation]:
        result = await db.execute(select(StoreLocationModel))
        store_locations = result.scalars().all()
        return [StoreLocation.model_validate(store_location) for store_location in store_locations]

    async def get_by_store_brand(self, store_brand_id: int, db: AsyncSession) -> List[StoreLocation]:
        result = await db.execute(
            select(StoreLocationModel).where(StoreLocationModel.store_brand_id == store_brand_id)
        )
        store_location = result.scalar_one_or_none()
        return StoreLocation.model_validate(store_location) if store_location else None

    async def update(self, location_id: int, store_location: StoreLocation, db: AsyncSession) -> Optional[StoreLocation]:
        try:
            result = await db.execute(
                select(StoreLocationModel).where(StoreLocationModel.id == location_id)
            )
            store_location_db = result.scalar_one_or_none()
            if store_location_db:
                store_location_db.name = store_location.name
                await db.flush()
                await db.commit()
                return StoreLocation.model_validate(store_location_db)
            logger.warning(f"Store location not found for update: {location_id}")
            return None
        except Exception as e:
            logger.error(f"Error updating store location {location_id}: {str(e)}")
            await db.rollback()
            raise

    async def delete(self, location_id: int, db: AsyncSession) -> bool:
        result = await db.execute(
            select(StoreLocationModel).where(StoreLocationModel.id == location_id)
        )
        store_location = result.scalar_one_or_none()
        if store_location:
            await db.delete(store_location)
            await db.flush()
            await db.commit()
            return True
        return False