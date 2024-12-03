from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
from app.domain.models import StoreBrand
from app.use_cases.store_brand_use_cases import StoreBrandUseCases
from app.infrastructure.database.database import get_db
from app.infrastructure.repositories.postgres_store_brand_repository import PostgresStoreBrandRepository

router = APIRouter(
    prefix="/store-brands",
    tags=["Store Brands"]
)

async def get_store_brand_use_cases(db: AsyncSession = Depends(get_db)):
    repository = PostgresStoreBrandRepository(db)
    return StoreBrandUseCases(repository)

@router.post("/store-brands", response_model=StoreBrand)
async def create_store_brand(
    name: str,
    use_cases: StoreBrandUseCases = Depends(get_store_brand_use_cases)
):
    return await use_cases.create_store_brand(name)

@router.get("/store-brands/{store_brand_id}", response_model=StoreBrand)
async def get_store_brand(
    store_brand_id: UUID,
    use_cases: StoreBrandUseCases = Depends(get_store_brand_use_cases)
):
    store_brand = await use_cases.get_store_brand(store_brand_id)
    if not store_brand:
        raise HTTPException(status_code=404, detail="Store brand not found")
    return store_brand

@router.get("/store-brands", response_model=List[StoreBrand])
async def get_all_store_brands(
    use_cases: StoreBrandUseCases = Depends(get_store_brand_use_cases)
):
    return await use_cases.get_all_store_brands()

@router.put("/store-brands/{store_brand_id}", response_model=StoreBrand)
async def update_store_brand(
    store_brand_id: UUID,
    name: str,
    use_cases: StoreBrandUseCases = Depends(get_store_brand_use_cases)
):
    store_brand = await use_cases.update_store_brand(store_brand_id, name)
    if not store_brand:
        raise HTTPException(status_code=404, detail="Store brand not found")
    return store_brand

@router.delete("/store-brands/{store_brand_id}")
async def delete_store_brand(
    store_brand_id: UUID,
    use_cases: StoreBrandUseCases = Depends(get_store_brand_use_cases)
):
    success = await use_cases.delete_store_brand(store_brand_id)
    if not success:
        raise HTTPException(status_code=404, detail="Store brand not found")
    return {"message": "Store brand deleted successfully"} 