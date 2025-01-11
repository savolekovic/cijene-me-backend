from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import asc, select
from typing import List, Optional
from app.domain.models.store.store_brand import StoreBrand
from app.domain.repositories.store.store_brand_repo import StoreBrandRepository
from app.infrastructure.database.models.store import StoreBrandModel, StoreLocationModel
from app.core.exceptions import DatabaseError, NotFoundError
from app.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)

class PostgresStoreBrandRepository(StoreBrandRepository):
    def __init__(self, session: AsyncSession = None):
        pass

    async def create(self, name: str, db: AsyncSession) -> StoreBrand:
        try:
            db_store_brand = StoreBrandModel(name=name)
            db.add(db_store_brand)
            await db.flush()
            await db.commit()

            return StoreBrand(
                id=db_store_brand.id,
                name=db_store_brand.name,
                created_at=db_store_brand.created_at
            )
        except Exception as e:
            logger.error(f"Error creating store brand: {str(e)}")
            await db.rollback()
            raise DatabaseError(f"Failed to create store brand: {str(e)}")

    async def get(self, store_brand_id: int, db: AsyncSession) -> Optional[StoreBrand]:
        try:
            result = await db.execute(
                select(StoreBrandModel).where(StoreBrandModel.id == store_brand_id)
            )
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

    async def update(self, store_brand_id: int, store_brand: StoreBrand, db: AsyncSession) -> Optional[StoreBrand]:
        try:
            result = await db.execute(
                select(StoreBrandModel).where(StoreBrandModel.id == store_brand_id)
            )
            db_store_brand = result.scalar_one_or_none()
            
            if db_store_brand:
                db_store_brand.name = store_brand.name
                await db.flush()
                await db.commit()
                return StoreBrand(
                    id=db_store_brand.id,
                    name=db_store_brand.name,
                    created_at=db_store_brand.created_at
                )
            return None
        except Exception as e:
            logger.error(f"Error updating store brand: {str(e)}")
            await db.rollback()
            raise DatabaseError(f"Failed to update store brand: {str(e)}")

    async def delete(self, store_brand_id: int, db: AsyncSession) -> bool:
        try:
            # First check if there are any associated store locations
            locations_result = await db.execute(
                select(StoreLocationModel).where(StoreLocationModel.store_brand_id == store_brand_id)
            )
            locations = locations_result.scalars().all()
            if locations:
                raise DatabaseError(
                    f"Cannot delete store brand {store_brand_id} because it has {len(locations)} associated store locations. "
                    "Please delete all store locations first."
                )

            # If no locations exist, proceed with deletion
            result = await db.execute(
                select(StoreBrandModel).where(StoreBrandModel.id == store_brand_id)
            )
            db_store_brand = result.scalar_one_or_none()
            
            if db_store_brand:
                await db.delete(db_store_brand)
                await db.flush()
                await db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting store brand: {str(e)}")
            await db.rollback()
            raise DatabaseError(f"Failed to delete store brand: {str(e)}")

    async def get_all(self, db: AsyncSession) -> List[StoreBrand]:
        try:
            result = await db.execute(
                select(StoreBrandModel).order_by(asc(StoreBrandModel.name))
            )
            brands = result.scalars().all()
            return [
                StoreBrand(
                    id=brand.id,
                    name=brand.name,
                    created_at=brand.created_at
                ) 
                for brand in brands
            ]
        except Exception as e:
            logger.error(f"Error getting all store brands: {str(e)}")
            raise DatabaseError(f"Failed to get store brands: {str(e)}")

    async def get_locations_for_brand(self, store_brand_id: int, db: AsyncSession) -> List[StoreLocationModel]:
        try:
            result = await db.execute(
                select(StoreLocationModel).where(StoreLocationModel.store_brand_id == store_brand_id)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting locations for store brand {store_brand_id}: {str(e)}")
            raise DatabaseError(f"Failed to get locations for store brand: {str(e)}") 