from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from decimal import Decimal
from app.domain.models.product import ProductEntry
from app.domain.models.auth import User
from app.infrastructure.database.database import get_db
from app.infrastructure.repositories.product.postgres_product_entry_repository import PostgresProductEntryRepository
from app.api.dependencies.auth import get_current_user
from app.core.exceptions import DatabaseError, NotFoundError, ValidationError

router = APIRouter(
    prefix="/product-entries",
    tags=["Product Entries"]
)

@router.post("/", 
    response_model=ProductEntry,
    summary="Create a new product entry",
    description="Create a new product price entry. Requires authentication.",
    responses={
        401: {
            "description": "Unauthorized - Invalid or missing authentication token",
            "content": {
                "application/json": {
                    "example": {"detail": "Could not validate credentials"}
                }
            }
        }
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
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        repository = PostgresProductEntryRepository(db)
        return await repository.create(
            product_id=product_id,
            store_brand_id=store_brand_id,
            store_location_id=store_location_id,
            price=price
        )
    except Exception as e:
        raise  # Let global error handler deal with it

@router.get("/", response_model=List[ProductEntry])
async def get_all_product_entries(
    db: AsyncSession = Depends(get_db)
):
    try:
        repository = PostgresProductEntryRepository(db)
        return await repository.get_all()
    except Exception as e:
        raise

@router.get("/product/{product_id}", response_model=List[ProductEntry])
async def get_product_entries_by_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        repository = PostgresProductEntryRepository(db)
        return await repository.get_by_product(product_id)
    except Exception as e:
        raise

@router.get("/store-brand/{store_brand_id}", response_model=List[ProductEntry])
async def get_product_entries_by_store_brand(
    store_brand_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        repository = PostgresProductEntryRepository(db)
        return await repository.get_by_store_brand(store_brand_id)
    except Exception as e:
        raise

@router.get("/store-location/{store_location_id}", response_model=List[ProductEntry])
async def get_product_entries_by_store_location(
    store_location_id: int,
    db: AsyncSession = Depends(get_db)
):
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
    try:
        repository = PostgresProductEntryRepository(db)
        return await repository.get(entry_id)
    except Exception as e:
        raise