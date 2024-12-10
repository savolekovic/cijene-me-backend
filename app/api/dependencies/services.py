from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.database import get_db
from app.services.auth_service import AuthService
from app.infrastructure.repositories.auth.postgres_user_repository import PostgresUserRepository
from app.infrastructure.repositories.product.postgres_category_repository import PostgresCategoryRepository
from app.infrastructure.repositories.product.postgres_product_repository import PostgresProductRepository
from app.infrastructure.repositories.product.postgres_product_entry_repository import PostgresProductEntryRepository
from app.infrastructure.repositories.store.postgres_store_brand_repository import PostgresStoreBrandRepository
from app.infrastructure.repositories.store.postgres_store_location_repository import PostgresStoreLocationRepository

async def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    """Get configured AuthService instance"""
    repository = PostgresUserRepository(db)
    return AuthService(repository)

async def get_category_repository(db: AsyncSession = Depends(get_db)) -> PostgresCategoryRepository:
    """Get configured CategoryRepository instance"""
    return PostgresCategoryRepository(db)

async def get_user_repository(db: AsyncSession = Depends(get_db)) -> PostgresUserRepository:
    """Get configured UserRepository instance"""
    return PostgresUserRepository(db)

async def get_product_repository(db: AsyncSession = Depends(get_db)) -> PostgresProductRepository:
    """Get configured ProductRepository instance"""
    return PostgresProductRepository(db)

async def get_product_entry_repository(db: AsyncSession = Depends(get_db)) -> PostgresProductEntryRepository:
    """Get configured ProductEntryRepository instance"""
    return PostgresProductEntryRepository(db)

async def get_store_brand_repository(db: AsyncSession = Depends(get_db)) -> PostgresStoreBrandRepository:
    """Get configured StoreBrandRepository instance"""
    return PostgresStoreBrandRepository(db)

async def get_store_location_repository(db: AsyncSession = Depends(get_db)) -> PostgresStoreLocationRepository:
    """Get configured StoreLocationRepository instance"""
    return PostgresStoreLocationRepository(db) 