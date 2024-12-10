from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal
from app.domain.models.product import ProductEntry
from app.domain.models.auth import User
from app.infrastructure.database.database import get_db
from app.infrastructure.repositories.product.postgres_product_entry_repository import PostgresProductEntryRepository
from app.api.dependencies.auth import get_current_privileged_user
from app.api.dependencies.services import get_product_entry_repository
from app.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/product-entries",
    tags=["Product Entries"]
)

@router.post("/", 
    response_model=ProductEntry,
    summary="Create a new product entry",
    description="Create a new product price entry. Requires admin or mediator role.",
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"}
    },
    openapi_extra={
        "security": [{"Bearer": []}]
    }
)
async def create_product_entry(
    product_id: int,
    store_brand_id: int,
    store_location_id: int,
    price: Decimal,
    current_user: User = Depends(get_current_privileged_user),
    entry_repo: PostgresProductEntryRepository = Depends(get_product_entry_repository)
):
    try:
        logger.info(f"Creating price entry: Product {product_id}, Store {store_brand_id}, Location {store_location_id}, Price {price}")
        entry = await entry_repo.create(
            product_id=product_id,
            store_brand_id=store_brand_id,
            store_location_id=store_location_id,
            price=price
        )
        logger.info(f"Created price entry with id: {entry.id}")
        return entry
    except Exception as e:
        logger.error(f"Error creating price entry: {str(e)}")
        raise

@router.get("/", response_model=List[ProductEntry])
async def get_all_product_entries(
    entry_repo: PostgresProductEntryRepository = Depends(get_product_entry_repository)
):
    logger.info("Fetching all price entries")
    return await entry_repo.get_all()

@router.get("/product/{product_id}", response_model=List[ProductEntry])
async def get_product_entries_by_product(
    product_id: int,
    entry_repo: PostgresProductEntryRepository = Depends(get_product_entry_repository)
):
    logger.info(f"Fetching price entries for product: {product_id}")
    return await entry_repo.get_by_product(product_id)

@router.get("/store-brand/{store_brand_id}", response_model=List[ProductEntry])
async def get_product_entries_by_store_brand(
    store_brand_id: int,
    entry_repo: PostgresProductEntryRepository = Depends(get_product_entry_repository)
):
    logger.info(f"Fetching price entries for store brand: {store_brand_id}")
    return await entry_repo.get_by_store_brand(store_brand_id)

@router.get("/store-location/{store_location_id}", response_model=List[ProductEntry])
async def get_product_entries_by_store_location(
    store_location_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all price entries for a specific store location. Public endpoint."""
    try:
        repository = PostgresProductEntryRepository(db)
        return await repository.get_by_store_location(store_location_id)
    except Exception as e:
        raise

@router.get("/{entry_id}", response_model=ProductEntry)
async def get_product_entry(
    entry_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific price entry by ID. Public endpoint."""
    try:
        repository = PostgresProductEntryRepository(db)
        return await repository.get(entry_id)
    except Exception as e:
        raise