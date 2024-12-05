from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging
from app.domain.models import StoreBrand
from app.infrastructure.database.database import get_db
from app.infrastructure.repositories.postgres_store_brand_repository import PostgresStoreBrandRepository

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/store-brands",
    tags=["Store Brands"]
)

@router.post("/", response_model=StoreBrand)
async def create_store_brand(
    name: str,
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
        store_brand = await repository.get(store_brand_id)
        if not store_brand:
            raise HTTPException(status_code=404, detail="Store brand not found")
        return store_brand
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting store brand: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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

@router.put("/{store_brand_id}", response_model=StoreBrand)
async def update_store_brand(
    store_brand_id: int,
    name: str,
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

@router.delete("/{store_brand_id}")
async def delete_store_brand(
    store_brand_id: int,
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