from dependency_injector import containers, providers
from app.services.cache_service import CacheManager
from app.services.product_service import ProductService
from app.infrastructure.repositories.product.postgres_product_repository import PostgresProductRepository
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
    
    # Services
    cache_manager = providers.Singleton(CacheManager)
    product_service = providers.Factory(
        ProductService,
        product_repo=product_repository,
        cache_manager=cache_manager
    ) 