from dependency_injector import containers, providers
from app.infrastructure.repositories.store.postgres_store_brand_repository import PostgresStoreBrandRepository
from app.infrastructure.repositories.store.postgres_store_location_repository import PostgresStoreLocationRepository
from app.services.cache_service import CacheManager
from app.services.product_service import ProductService
from app.services.store_brand_service import StoreBrandService
from app.services.store_location_service import StoreLocationService
from app.services.user_service import UserService
from app.services.category_service import CategoryService
from app.services.product_entry_service import ProductEntryService
from app.infrastructure.repositories.product.postgres_product_repository import PostgresProductRepository
from app.infrastructure.repositories.auth.postgres_user_repository import PostgresUserRepository
from app.infrastructure.repositories.product.postgres_category_repository import PostgresCategoryRepository
from app.infrastructure.repositories.product.postgres_product_entry_repository import PostgresProductEntryRepository
from app.infrastructure.database.database import AsyncSessionLocal
from app.services.auth_service import AuthService

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    
    # Database
    db = providers.Resource(
        AsyncSessionLocal
    )
    
    # Repositories
    product_repository = providers.Factory(
        PostgresProductRepository,
        session=db
    )
    
    product_entry_repository = providers.Factory(
        PostgresProductEntryRepository,
        session=db
    )
    
    user_repository = providers.Factory(
        PostgresUserRepository,
        session=db
    )
    
    category_repository = providers.Factory(
        PostgresCategoryRepository,
        session=db
    )
    
    store_brand_repository = providers.Factory(
        PostgresStoreBrandRepository,
        session=db
    )
    
    store_location_repository = providers.Factory(
        PostgresStoreLocationRepository,
        session=db
    )
    
    # Services
    cache_manager = providers.Singleton(CacheManager)
    
    product_service = providers.Factory(
        ProductService,
        product_repo=product_repository,
        category_repo=category_repository,
        cache_manager=cache_manager
    )
    
    product_entry_service = providers.Factory(
        ProductEntryService,
        product_entry_repo=product_entry_repository,
        store_location_repo=store_location_repository,
        cache_manager=cache_manager
    ) 
    
    user_service = providers.Factory(
        UserService,
        user_repo=user_repository,
        cache_manager=cache_manager
    )
    
    category_service = providers.Factory(
        CategoryService,
        category_repo=category_repository,
        cache_manager=cache_manager
    )
    
    store_brand_service = providers.Factory(
        StoreBrandService,
        store_brand_repo=store_brand_repository,
        cache_manager=cache_manager
    ) 
    
    store_location_service = providers.Factory(
        StoreLocationService,
        store_location_repo=store_location_repository,
        cache_manager=cache_manager
    ) 
    
    auth_service = providers.Factory(
        AuthService,
        user_repo=user_repository
    )
