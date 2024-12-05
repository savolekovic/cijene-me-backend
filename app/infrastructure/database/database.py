from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
import logging
from urllib.parse import quote_plus
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create Base class for models
Base = declarative_base()

# URL encode the password
password = quote_plus(os.getenv('DATABASE_PASSWORD', ''))
DATABASE_URL = f"postgresql+asyncpg://{os.getenv('DATABASE_USER')}:{password}@localhost:5432/{os.getenv('DATABASE_NAME')}"

logger.info("Attempting to connect to database...")

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
)

# Create async session maker
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Dependency for FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Note: Required environment variables:
# - DATABASE_USER
# - DATABASE_PASSWORD
# - DATABASE_HOST
# - DATABASE_NAME