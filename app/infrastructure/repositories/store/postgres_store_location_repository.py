from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, asc
from typing import List, Optional
from app.core.exceptions import DatabaseError
from app.domain.models.store.store_location import StoreLocation
from app.domain.repositories.store.store_location_repo import StoreLocationRepository
from app.infrastructure.database.models.store import StoreBrandModel, StoreLocationModel
from app.infrastructure.logging.logger import get_logger
from app.api.responses.store import StoreLocationWithBrandResponse, StoreBrandInLocation

logger = get_logger(__name__)

class PostgresStoreLocationRepository(StoreLocationRepository):
    def __init__(self, session: AsyncSession = None):
        self.session = session

    async def create(self, store_brand_id: int, address: str, db: AsyncSession) -> StoreLocation:
        try:
            # Check for existing location with same address and brand
            existing_location = await db.execute(
                select(StoreLocationModel)
                .where(
                    StoreLocationModel.store_brand_id == store_brand_id,
                    StoreLocationModel.address == address
                )
            )
            if existing_location.scalar_one_or_none():
                raise DatabaseError(f"Store location already exists for brand {store_brand_id} at address: {address}")

            db_store_location = StoreLocationModel(
                store_brand_id=store_brand_id,
                address=address
            )
            db.add(db_store_location)
            await db.flush()
            await db.commit()

            return StoreLocation.model_validate(db_store_location)
        except DatabaseError:
            await db.rollback()
            raise
        except Exception as e:
            logger.error(f"Error creating store location: {str(e)}")
            await db.rollback()
            raise DatabaseError(f"Failed to create store location: {str(e)}")

    async def get(self, location_id: int, db: AsyncSession) -> Optional[StoreLocationWithBrandResponse]:
        try:
            query = (
                select(
                    StoreLocationModel,
                    StoreBrandModel
                )
                .join(StoreBrandModel)
                .where(StoreLocationModel.id == location_id)
            )
            result = await db.execute(query)
            location = result.first()
            
            if location:
                return StoreLocationWithBrandResponse(
                    id=location[0].id,
                    address=location[0].address,
                    created_at=location[0].created_at,
                    store_brand=StoreBrandInLocation(
                        id=location[1].id,
                        name=location[1].name
                    )
                )
            return None
        except Exception as e:
            logger.error(f"Error getting store location: {str(e)}")
            raise DatabaseError(f"Failed to get store location: {str(e)}")

    async def get_all(self, db: AsyncSession) -> List[StoreLocationWithBrandResponse]:
        try:
            query = (
                select(
                    StoreLocationModel,
                    StoreBrandModel
                )
                .join(StoreBrandModel)
                .order_by(asc(StoreLocationModel.id))
            )
            result = await db.execute(query)
            locations = result.all()
            
            return [
                StoreLocationWithBrandResponse(
                    id=location[0].id,
                    address=location[0].address,
                    created_at=location[0].created_at,
                    store_brand=StoreBrandInLocation(
                        id=location[1].id,
                        name=location[1].name
                    )
                )
                for location in locations
            ]
        except Exception as e:
            logger.error(f"Error getting store locations: {str(e)}")
            raise DatabaseError(f"Failed to get store locations: {str(e)}")

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