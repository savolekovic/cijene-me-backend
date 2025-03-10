from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, asc, func, or_, desc
from typing import List, Optional
from app.core.exceptions import DatabaseError
from app.domain.models.store.store_location import StoreLocation
from app.domain.repositories.store.store_location_repo import StoreLocationRepository
from app.infrastructure.database.models.store import StoreBrandModel, StoreLocationModel
from app.infrastructure.database.models.product import ProductEntryModel
from app.infrastructure.logging.logger import get_logger
from app.api.responses.store import StoreBrandInLocation, StoreLocationResponse, PaginatedStoreLocationResponse, SimpleStoreLocationResponse

logger = get_logger(__name__)

class PostgresStoreLocationRepository(StoreLocationRepository):
    def __init__(self, session: AsyncSession = None):
        self.session = session

    async def create(self, store_brand_id: int, address: str, db: AsyncSession) -> StoreLocationResponse:
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

            # Load store brand details
            query = (
                select(StoreLocationModel, StoreBrandModel)
                .join(StoreBrandModel, StoreLocationModel.store_brand_id == StoreBrandModel.id)
                .where(StoreLocationModel.id == db_store_location.id)
            )
            result = await db.execute(query)
            location, brand = result.first()
            await db.commit()

            return StoreLocationResponse(
                id=location.id,
                address=location.address,
                created_at=location.created_at,
                store_brand=StoreBrandInLocation(
                    id=brand.id,
                    name=brand.name
                )
            )
        except DatabaseError:
            await db.rollback()
            raise
        except Exception as e:
            logger.error(f"Error creating store location: {str(e)}")
            await db.rollback()
            raise DatabaseError(f"Failed to create store location: {str(e)}")

    async def get(self, location_id: int, db: AsyncSession) -> Optional[StoreLocationResponse]:
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
                return StoreLocationResponse(
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

    async def get_all(self, db: AsyncSession, page: int = 1, per_page: int = 10, search: str = None, order_by: str = "address", order_direction: str = "asc") -> PaginatedStoreLocationResponse:
        try:
            # Base query for data
            query = (
                select(StoreLocationModel, StoreBrandModel)
                .join(StoreBrandModel)
            )
            
            # Base query for count
            count_query = (
                select(StoreLocationModel)
                .join(StoreBrandModel)
            )
            
            # Add search filter if search query is provided
            if search:
                search_pattern = f"%{search}%"
                search_filter = or_(
                    StoreLocationModel.address.ilike(search_pattern),
                    StoreBrandModel.name.ilike(search_pattern)
                )
                query = query.where(search_filter)
                count_query = count_query.where(search_filter)
            
            # Get total count
            count_result = await db.execute(select(func.count()).select_from(count_query.subquery()))
            total_count = count_result.scalar()
            
            # Add ordering
            if order_by == "store_brand":
                order_column = StoreBrandModel.name
            else:
                order_column = getattr(StoreLocationModel, order_by, StoreLocationModel.address)
            
            if order_direction.lower() == "desc":
                query = query.order_by(desc(order_column))
            else:
                query = query.order_by(asc(order_column))
            
            # Add pagination
            offset = (page - 1) * per_page
            query = query.offset(offset).limit(per_page)
            
            # Get paginated data
            result = await db.execute(query)
            locations = result.all()
            
            # Convert to response model
            location_list = [
                StoreLocationResponse(
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
            
            return PaginatedStoreLocationResponse(
                total_count=total_count,
                data=location_list
            )
        except Exception as e:
            logger.error(f"Error getting store locations: {str(e)}")
            raise DatabaseError(f"Failed to get store locations: {str(e)}")

    async def get_by_store_brand(self, store_brand_id: int, db: AsyncSession) -> List[StoreLocation]:
        try:
            result = await db.execute(
                select(StoreLocationModel).where(StoreLocationModel.store_brand_id == store_brand_id)
            )
            locations = result.scalars().all()
            if not locations:
                logger.warning(f"No locations found for store brand {store_brand_id}")
            return [StoreLocation.model_validate(location) for location in locations]
        except Exception as e:
            logger.error(f"Error getting locations by store brand {store_brand_id}: {str(e)}")
            raise DatabaseError(f"Failed to get locations by store brand: {str(e)}")

    async def update(self, location_id: int, store_location: StoreLocation, db: AsyncSession) -> Optional[StoreLocationResponse]:
        try:
            # Get existing location
            result = await db.execute(
                select(StoreLocationModel).where(StoreLocationModel.id == location_id)
            )
            db_store_location = result.scalar_one_or_none()
            
            if db_store_location:
                # Update fields
                db_store_location.store_brand_id = store_location.store_brand_id
                db_store_location.address = store_location.address
                await db.flush()

                # Load store brand details for response
                query = (
                    select(StoreLocationModel, StoreBrandModel)
                    .join(StoreBrandModel, StoreLocationModel.store_brand_id == StoreBrandModel.id)
                    .where(StoreLocationModel.id == location_id)
                )
                result = await db.execute(query)
                location, brand = result.first()
                await db.commit()

                return StoreLocationResponse(
                    id=location.id,
                    address=location.address,
                    created_at=location.created_at,
                    store_brand=StoreBrandInLocation(
                        id=brand.id,
                        name=brand.name
                    )
                )
            return None
        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating store location: {str(e)}")
            raise DatabaseError(f"Failed to update store location: {str(e)}")

    async def delete(self, location_id: int, db: AsyncSession) -> bool:
        try:
            result = await db.execute(
                select(StoreLocationModel).where(StoreLocationModel.id == location_id)
            )
            store_location = result.scalar_one_or_none()
            if store_location:
                await db.delete(store_location)
                await db.flush()
                await db.commit()
                return True
            logger.warning(f"Store location not found for deletion: {location_id}")
            return False
        except Exception as e:
            logger.error(f"Error deleting store location {location_id}: {str(e)}")
            await db.rollback()
            raise DatabaseError(f"Failed to delete store location: {str(e)}")

    async def get_product_entries_for_location(self, location_id: int, db: AsyncSession) -> List[ProductEntryModel]:
        try:
            result = await db.execute(
                select(ProductEntryModel).where(ProductEntryModel.store_location_id == location_id)
            )
            entries = result.scalars().all()
            if not entries:
                logger.warning(f"No product entries found for location {location_id}")
            return entries
        except Exception as e:
            logger.error(f"Error getting product entries for location {location_id}: {str(e)}")
            raise DatabaseError(f"Failed to get product entries for location: {str(e)}")

    async def get_by_brand(self, store_brand_id: int, db: AsyncSession) -> List[StoreLocation]:
        try:
            result = await db.execute(
                select(StoreLocationModel).where(StoreLocationModel.store_brand_id == store_brand_id)
            )
            locations = result.scalars().all()
            return [
                StoreLocation(
                    id=location.id,
                    address=location.address,
                    store_brand_id=location.store_brand_id,
                    created_at=location.created_at
                ) for location in locations
            ]
        except Exception as e:
            logger.error(f"Error getting store locations by brand {store_brand_id}: {str(e)}")
            raise DatabaseError(f"Failed to get store locations by brand: {str(e)}")

    async def get_all_simple(self, db: AsyncSession, search: str = None, store_brand_id: int = None) -> List[SimpleStoreLocationResponse]:
        try:
            # Base query
            query = (
                select(StoreLocationModel, StoreBrandModel.name.label('store_brand_name'))
                .join(StoreBrandModel)
            )
            
            # Add search filter if search query is provided
            if search:
                search_pattern = f"%{search}%"
                search_filter = or_(
                    StoreLocationModel.address.ilike(search_pattern),
                    StoreBrandModel.name.ilike(search_pattern)
                )
                query = query.where(search_filter)
            
            # Add store brand filter if provided
            if store_brand_id:
                query = query.where(StoreLocationModel.store_brand_id == store_brand_id)
            
            # Add ordering
            query = query.order_by(StoreBrandModel.name, StoreLocationModel.address)
            
            # Get data
            result = await db.execute(query)
            locations = result.all()
            
            # Convert to response model
            return [
                SimpleStoreLocationResponse(
                    id=location[0].id,
                    address=location[0].address,
                    store_brand_name=location[1]
                )
                for location in locations
            ]
        except Exception as e:
            logger.error(f"Error getting simplified store locations list: {str(e)}")
            raise DatabaseError(f"Failed to get simplified store locations list: {str(e)}")