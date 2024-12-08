from app.infrastructure.database.database import engine, Base
from app.infrastructure.database.models.auth import UserModel
from app.infrastructure.database.models.store import StoreBrandModel, StoreLocationModel
from app.infrastructure.database.models.product import CategoryModel, ProductModel, ProductEntryModel
import logging
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_tables():
    try:
        logger.info("Starting table creation...")
        logger.info(f"Models to create: {Base.metadata.tables.keys()}")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Tables created successfully!")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(create_tables()) 