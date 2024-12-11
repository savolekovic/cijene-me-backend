from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.infrastructure.database.database import DATABASE_URL, get_db
import logging
import os

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Health"])

@router.get("/health", include_in_schema=False)
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        # Log connection attempt
        logger.info("Attempting database connection check")
        
        # Test database connection
        query = text("SELECT 1")
        await db.execute(query)
        
        logger.info("Database connection successful")
        return {
            "status": "healthy",
            "database": "connected",
            "environment": os.getenv('ENV', 'unknown')
        }
    except Exception as e:
        # Log the full error
        logger.error(f"Database connection failed: {str(e)}", exc_info=True)
        return {
            "status": "unhealthy",
            "database": str(e),
            "environment": os.getenv('ENV', 'unknown'),
            "database_url": DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'invalid_url'
        } 