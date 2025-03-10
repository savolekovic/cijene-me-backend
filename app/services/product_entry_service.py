from app.api.responses.product_entry import ProductEntryWithDetails, PaginatedProductEntryResponse
from app.domain.repositories.product.product_entry_repo import ProductEntryRepository
from app.domain.repositories.store.store_location_repo import StoreLocationRepository
from app.services.cache_service import CacheManager
from app.infrastructure.logging.logger import get_logger
from app.core.exceptions import NotFoundError
from typing import List
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.repositories.product.postgres_product_entry_repository import PostgresProductEntryRepository
from datetime import datetime

logger = get_logger(__name__)

class ProductEntryService:
    def __init__(
        self,
        store_location_repo: StoreLocationRepository,
        cache_manager: CacheManager,
        product_entry_repo: ProductEntryRepository = PostgresProductEntryRepository()
    ):
        self.product_entry_repo = product_entry_repo
        self.store_location_repo = store_location_repo
        self.cache_manager = cache_manager

    async def create_product_entry(
        self, 
        product_id: int,
        store_location_id: int,
        price: Decimal,
        db: AsyncSession
    ) -> ProductEntryWithDetails:
        try:
            # Get store location to verify it exists and get store_brand_id
            store_location = await self.store_location_repo.get(store_location_id, db)
            if not store_location:
                raise NotFoundError("Store Location", store_location_id)

            # Create entry with store_brand_id from the location's store_brand
            entry = await self.product_entry_repo.create(
                product_id=product_id,
                store_brand_id=store_location.store_brand.id,
                store_location_id=store_location_id,
                price=price,
                db=db
            )
            await self.cache_manager.clear_product_related_caches()
            return entry
        except Exception as e:
            logger.error(f"Error creating product entry: {str(e)}")
            raise

    async def get_all_product_entries(
        self, 
        db: AsyncSession, 
        page: int = 1, 
        per_page: int = 10,
        search: str = None,
        product_id: int = None,
        store_brand_id: int = None,
        store_location_id: int = None,
        min_price: float = None,
        max_price: float = None,
        from_date: datetime = None,
        to_date: datetime = None,
        order_by: str = "created_at",
        order_direction: str = "desc"
    ) -> PaginatedProductEntryResponse:
        """
        Get all product entries with pagination and filtering options.
        
        Args:
            db: Database session
            page: Page number (default: 1)
            per_page: Number of items per page (default: 10)
            search: Optional search query
            product_id: Optional product ID filter
            store_brand_id: Optional store brand ID filter
            store_location_id: Optional store location ID filter
            min_price: Optional minimum price filter
            max_price: Optional maximum price filter
            from_date: Optional start date filter
            to_date: Optional end date filter
            order_by: Field to order by (default: created_at)
            order_direction: Order direction (asc or desc) (default: desc)
            
        Returns:
            PaginatedProductEntryResponse containing the filtered and paginated list of product entries
        """
        logger.info(f"Getting product entries - page: {page}, per_page: {per_page}, search: {search}, " +
                   f"product_id: {product_id}, store_brand_id: {store_brand_id}, " +
                   f"store_location_id: {store_location_id}, min_price: {min_price}, " +
                   f"max_price: {max_price}, from_date: {from_date}, to_date: {to_date}, " +
                   f"order_by: {order_by}, order_direction: {order_direction}")
        
        return await self.product_entry_repo.get_all(
            db=db, 
            page=page, 
            per_page=per_page, 
            search=search,
            product_id=product_id,
            store_brand_id=store_brand_id,
            store_location_id=store_location_id,
            min_price=min_price,
            max_price=max_price,
            from_date=from_date,
            to_date=to_date,
            order_by=order_by,
            order_direction=order_direction
        )

    async def get_entry(self, entry_id: int, db: AsyncSession) -> ProductEntryWithDetails:
        try:
            logger.info(f"Fetching price entry with id: {entry_id}")
            entry = await self.product_entry_repo.get(entry_id, db)
            if not entry:
                logger.warning(f"Price entry not found: {entry_id}")
                raise NotFoundError("Price entry", entry_id)
            return entry
        except Exception as e:
            logger.error(f"Error fetching price entry {entry_id}: {str(e)}")
            raise

    async def get_entries_by_product(self, product_id: int, db: AsyncSession) -> List[ProductEntryWithDetails]:
        try:
            logger.info(f"Fetching price entries for product: {product_id}")
            return await self.product_entry_repo.get_by_product(product_id, db)
        except Exception as e:
            logger.error(f"Error fetching price entries for product {product_id}: {str(e)}")
            raise

    async def get_entries_by_store_brand(self, store_brand_id: int, db: AsyncSession) -> List[ProductEntryWithDetails]:
        try:
            logger.info(f"Fetching price entries for store brand: {store_brand_id}")
            return await self.product_entry_repo.get_by_store_brand(store_brand_id, db)
        except Exception as e:
            logger.error(f"Error fetching price entries for store brand {store_brand_id}: {str(e)}")
            raise

    async def get_entries_by_store_location(self, store_location_id: int, db: AsyncSession) -> List[ProductEntryWithDetails]:
        try:
            logger.info(f"Fetching price entries for store location: {store_location_id}")
            return await self.product_entry_repo.get_by_store_location(store_location_id, db)
        except Exception as e:
            logger.error(f"Error fetching price entries for store location {store_location_id}: {str(e)}")
            raise

    async def delete_entry(self, entry_id: int, db: AsyncSession) -> bool:
        try:
            logger.info(f"Attempting to delete product entry {entry_id}")
            
            # First check if entry exists
            entry = await self.product_entry_repo.get(entry_id, db)
            if not entry:
                logger.warning(f"Product entry not found: {entry_id}")
                raise NotFoundError("Product entry", entry_id)
            
            success = await self.product_entry_repo.delete(entry_id, db)
            logger.info(f"Successfully deleted product entry {entry_id}")
            await self.cache_manager.clear_product_related_caches()
            return True
        except Exception as e:
            logger.error(f"Error deleting product entry {entry_id}: {str(e)}")
            raise

    async def get_price_statistics(self, product_id: int, db: AsyncSession) -> dict:
        try:
            logger.info(f"Calculating price statistics for product: {product_id}")
            
            # Fetch all entries for the product
            entries = await self.product_entry_repo.get_by_product(product_id, db)
            
            if not entries:
                return {
                    "lowest_price": None,
                    "highest_price": None,
                    "average_price": None,
                    "latest_price": None,
                    "total_entries": 0,
                    "first_entry_date": None,
                    "latest_entry_date": None,
                    "price_change": None,
                    "price_change_percentage": None
                }
            
            # Sort entries by created_at to ensure correct order
            sorted_entries = sorted(entries, key=lambda x: x.created_at)
            prices = [float(entry.price) for entry in sorted_entries]
            
            # Basic statistics
            lowest_price = min(prices)
            highest_price = max(prices)
            average_price = sum(prices) / len(prices)
            latest_price = prices[-1]
            first_price = prices[0]
            
            # Calculate price change
            price_change = latest_price - first_price
            price_change_percentage = (price_change / first_price) * 100 if first_price > 0 else 0
            
            return {
                "lowest_price": lowest_price,
                "highest_price": highest_price,
                "average_price": round(average_price, 2),
                "latest_price": latest_price,
                "total_entries": len(entries),
                "first_entry_date": sorted_entries[0].created_at,
                "latest_entry_date": sorted_entries[-1].created_at,
                "price_change": round(price_change, 2),
                "price_change_percentage": round(price_change_percentage, 2)
            }
        except Exception as e:
            logger.error(f"Error calculating price statistics for product {product_id}: {str(e)}")
            raise
