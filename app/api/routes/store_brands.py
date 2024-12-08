from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging
from app.domain.models.store import StoreBrand
from app.domain.models.auth import User
from app.infrastructure.database.database import get_db
from app.infrastructure.repositories.store.postgres_store_brand_repository import PostgresStoreBrandRepository
from app.api.dependencies.auth import get_current_admin
from app.core.exceptions import DatabaseError, NotFoundError, ValidationError

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/store-brands",
    tags=["Store Brands"]
)

# Common response definition
unauthorized_response = {
    401: {
        "description": "Unauthorized - Invalid or missing authentication token",
        "content": {
            "application/json": {
                "example": {"detail": "Could not validate credentials"}
            }
        }
    }
}

@router.post("/", 
    response_model=StoreBrand,
    summary="Create a new store brand",
    description="Create a new store brand. Requires admin authentication.",
    responses=unauthorized_response,
    openapi_extra={
        "security": [{"Bearer": []}]
    }
)
async def create_store_brand(
    name: str,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        repository = PostgresStoreBrandRepository(db)
        return await repository.create(name)
    except Exception as e:
        logger.error(f"Error creating store brand: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{store_brand_id}", response_model=StoreBrand)
async def get_store_brand(
    store_brand_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        repository = PostgresStoreBrandRepository(db)
        return await repository.get(store_brand_id)
    except Exception as e:
        logger.error(f"Error getting store brand: {str(e)}")
        raise  # Let the global handler deal with it

@router.get("/", response_model=List[StoreBrand])
async def get_all_store_brands(
    db: AsyncSession = Depends(get_db)
):
    try:
        repository = PostgresStoreBrandRepository(db)
        return await repository.get_all()
    except Exception as e:
        logger.error(f"Error getting all store brands: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{store_brand_id}", 
    response_model=StoreBrand,
    summary="Update a store brand",
    description="Update an existing store brand. Requires authentication.",
    responses=unauthorized_response,
    openapi_extra={
        "security": [{"Bearer": []}]
    }
)
async def update_store_brand(
    store_brand_id: int,
    name: str,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        repository = PostgresStoreBrandRepository(db)
        store_brand = StoreBrand(id=store_brand_id, name=name)
        updated_store_brand = await repository.update(store_brand_id, store_brand)
        if not updated_store_brand:
            raise HTTPException(status_code=404, detail="Store brand not found")
        return updated_store_brand
    except Exception as e:
        logger.error(f"Error updating store brand: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{store_brand_id}",
    summary="Delete a store brand",
    description="Delete an existing store brand. Requires authentication.",
    responses=unauthorized_response,
    openapi_extra={
        "security": [{"Bearer": []}]
    }
)
async def delete_store_brand(
    store_brand_id: int,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        repository = PostgresStoreBrandRepository(db)
        success = await repository.delete(store_brand_id)
        if not success:
            raise HTTPException(status_code=404, detail="Store brand not found")
        return {"message": "Store brand deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting store brand: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 