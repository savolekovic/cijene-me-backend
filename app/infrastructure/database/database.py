from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
import logging
import os
from urllib.parse import quote_plus
import ssl

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create Base class for models
Base = declarative_base()

# Get environment
ENV = os.getenv('ENV', 'production')  # Default to development if not specified
logger.info(f"Current environment: {ENV}")

# Define timezone constant - Montenegro is UTC+1 (or UTC+2 in summer)
TIMEZONE_OFFSET = timedelta(hours=1)  # or hours=2 during summer time

def get_current_time():
    """Get current time in Montenegro timezone"""
    return datetime.now(timezone(TIMEZONE_OFFSET))

if ENV == 'production':
    # Use Neon.tech database URL
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is required in production")
    
    # Convert the URL to asyncpg format
    if DATABASE_URL.startswith('postgresql://'):
        DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://', 1)
    
    # Remove sslmode from URL if present
    if '?' in DATABASE_URL:
        base_url = DATABASE_URL.split('?')[0]
        DATABASE_URL = base_url
    
    # Log the connection attempt (without password)
    safe_url = DATABASE_URL.split('@')[1]
    logger.info(f"Connecting to production database: {safe_url}")
    
    # Create SSL context
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    # Create engine with SSL for production
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        connect_args={"ssl": ssl_context}
    )
else:
    # Local development database
    # URL encode the password
    password = quote_plus(os.getenv('DB_PASSWORD', ''))
    DATABASE_URL = f"postgresql+asyncpg://{os.getenv('DB_USER')}:{password}@{os.getenv('DB_HOST')}:5432/{os.getenv('DB_NAME')}"
    logger.info(f"Connecting to database with encoded password")
    
    # Create engine without SSL for local development
    engine = create_async_engine(
        DATABASE_URL,
        echo=True
    )

logger.info(f"Using database for environment: {ENV}")

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