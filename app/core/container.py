from dependency_injector import containers, providers
from app.services.cache_service import CacheManager
from app.services.product_service import ProductService
from app.services.user_service import UserService
from app.services.category_service import CategoryService
from app.infrastructure.repositories.product.postgres_product_repository import PostgresProductRepository
from app.infrastructure.repositories.auth.postgres_user_repository import PostgresUserRepository
from app.infrastructure.repositories.product.postgres_category_repository import PostgresCategoryRepository
from app.infrastructure.database.database import AsyncSessionLocal

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
    
    user_repository = providers.Factory(
        PostgresUserRepository,
        session=db
    )
    
    category_repository = providers.Factory(
        PostgresCategoryRepository,
        session=db
    )
    
    # Services
    cache_manager = providers.Singleton(CacheManager)
    
    product_service = providers.Factory(
        ProductService,
        product_repo=product_repository,
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