from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, asc
from typing import List, Optional
from app.domain.models.store.store_brand import StoreBrand
from app.domain.repositories.store.store_brand_repo import StoreBrandRepository
from app.infrastructure.database.models.store import StoreBrandModel, StoreLocationModel
from app.core.exceptions import DatabaseError, NotFoundError
from app.infrastructure.logging.logger import get_logger
from app.api.responses.store import StoreBrandResponse, PaginatedStoreBrandResponse, SimpleStoreBrandResponse

logger = get_logger(__name__)

class PostgresStoreBrandRepository(StoreBrandRepository):
    def __init__(self, session: AsyncSession = None):
        self.session = session

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
            logger.error(f"Error getting store brand {store_brand_id}: {str(e)}")
            raise DatabaseError(f"Failed to get store brand: {str(e)}")

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

    async def get_all(self, db: AsyncSession, page: int = 1, per_page: int = 10, search: str = None, order_by: str = "name", order_direction: str = "asc") -> PaginatedStoreBrandResponse:
        try:
            # Base query for data
            query = select(StoreBrandModel)
            
            # Base query for count
            count_query = select(StoreBrandModel)
            
            # Add search filter if search query is provided
            if search:
                search_pattern = f"%{search}%"
                search_filter = StoreBrandModel.name.ilike(search_pattern)
                query = query.where(search_filter)
                count_query = count_query.where(search_filter)
            
            # Get total count
            count_result = await db.execute(select(func.count()).select_from(count_query.subquery()))
            total_count = count_result.scalar()
            
            # Add ordering
            order_column = getattr(StoreBrandModel, order_by, StoreBrandModel.name)
            if order_direction.lower() == "desc":
                query = query.order_by(desc(order_column))
            else:
                query = query.order_by(asc(order_column))
            
            # Add pagination
            offset = (page - 1) * per_page
            query = query.offset(offset).limit(per_page)
            
            # Get paginated data
            result = await db.execute(query)
            store_brands = result.scalars().all()
            
            # Convert to response model
            store_brand_list = [
                StoreBrandResponse(
                    id=brand.id,
                    name=brand.name,
                    created_at=brand.created_at
                )
                for brand in store_brands
            ]
            
            return PaginatedStoreBrandResponse(
                total_count=total_count,
                data=store_brand_list
            )
        except Exception as e:
            logger.error(f"Error getting store brands: {str(e)}")
            raise DatabaseError(f"Failed to get store brands: {str(e)}")

    async def get_locations_for_brand(self, store_brand_id: int, db: AsyncSession) -> List[StoreLocationModel]:
        try:
            result = await db.execute(
                select(StoreLocationModel).where(StoreLocationModel.store_brand_id == store_brand_id)
            )
            locations = result.scalars().all()
            if not locations:
                logger.warning(f"No locations found for store brand {store_brand_id}")
            return locations
        except Exception as e:
            logger.error(f"Error getting locations for store brand {store_brand_id}: {str(e)}")
            raise DatabaseError(f"Failed to get locations for store brand: {str(e)}")

    async def get_by_name(self, name: str, db: AsyncSession) -> Optional[StoreBrand]:
        try:
            result = await db.execute(
                select(StoreBrandModel).where(StoreBrandModel.name.ilike(name))
            )
            db_store_brand = result.scalar_one_or_none()
            
            if db_store_brand:
                return StoreBrand(
                    id=db_store_brand.id,
                    name=db_store_brand.name,
                    created_at=db_store_brand.created_at
                )
            return None
        except Exception as e:
            logger.error(f"Error getting store brand by name: {str(e)}")
            raise DatabaseError(f"Failed to get store brand by name: {str(e)}")

    async def get_all_simple(self, db: AsyncSession, search: str = None) -> List[SimpleStoreBrandResponse]:
        try:
            # Base query
            query = select(StoreBrandModel)
            
            # Add search filter if search query is provided
            if search:
                search_pattern = f"%{search}%"
                query = query.where(StoreBrandModel.name.ilike(search_pattern))
            
            # Add ordering
            query = query.order_by(StoreBrandModel.name)
            
            # Get data
            result = await db.execute(query)
            store_brands = result.scalars().all()
            
            # Convert to response model
            return [
                SimpleStoreBrandResponse(
                    id=brand.id,
                    name=brand.name
                )
                for brand in store_brands
            ]
        except Exception as e:
            logger.error(f"Error getting simplified store brands list: {str(e)}")
            raise DatabaseError(f"Failed to get simplified store brands list: {str(e)}") 