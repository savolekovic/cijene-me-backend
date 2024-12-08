from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.domain.models.product.category import Category
from app.infrastructure.database.database import get_db
from app.infrastructure.repositories.product.postgres_category_repository import PostgresCategoryRepository

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)

@router.get("/", response_model=List[Category])
async def get_all_categories(
    db: AsyncSession = Depends(get_db)
):
    repository = PostgresCategoryRepository(db)
    return await repository.get_all() 