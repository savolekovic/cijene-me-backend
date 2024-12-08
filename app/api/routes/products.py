from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.domain.models.product import Product, ProductWithCategory
from app.infrastructure.database.database import get_db
from app.infrastructure.repositories.product.postgres_product_repository import PostgresProductRepository

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

@router.get("/", response_model=List[ProductWithCategory])
async def get_all_products(
    db: AsyncSession = Depends(get_db)
):
    repository = PostgresProductRepository(db)
    return await repository.get_all_with_categories() 