from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.domain.models.product import Category
from app.domain.models.auth import User
from app.infrastructure.database.database import get_db
from app.infrastructure.repositories.product.postgres_category_repository import PostgresCategoryRepository
from app.api.dependencies.auth import get_current_privileged_user
from app.api.dependencies.services import get_category_repository
from app.core.exceptions import NotFoundError
from app.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)

@router.post("/", 
    response_model=Category,
    summary="Create a new category",
    description="Create a new category. Requires admin or mediator role.",
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden - Insufficient privileges"}
    },
    openapi_extra={
        "security": [{"Bearer": []}]
    }

)
async def create_category(
    name: str,
    current_user: User = Depends(get_current_privileged_user),
    category_repo: PostgresCategoryRepository = Depends(get_category_repository)
):
    try:
        logger.info(f"Creating new category: {name}")
        category = await category_repo.create(name=name)
        logger.info(f"Created category with id: {category.id}")
        return category
    except Exception as e:
        logger.error(f"Error creating category: {str(e)}")
        raise

@router.get("/", response_model=List[Category])
async def get_all_categories(
    category_repo: PostgresCategoryRepository = Depends(get_category_repository)
):
    logger.info("Fetching all categories")
    return await category_repo.get_all() 

@router.put("/{category_id}", 
    response_model=Category,
    summary="Update a category",
    description="Update an existing category. Requires admin or mediator role.",
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden - Insufficient privileges"},
        404: {"description": "Category not found"}
    },
    openapi_extra={
        "security": [{"Bearer": []}]
    }
)
async def update_category(
    category_id: int,
    name: str,
    current_user: User = Depends(get_current_privileged_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        repository = PostgresCategoryRepository(db)
        category = Category(id=category_id, name=name)
        updated_category = await repository.update(category_id, category)
        if not updated_category:
            raise NotFoundError("Category", category_id)
        return updated_category
    except Exception as e:
        raise

@router.delete("/{category_id}",
    summary="Delete a category",
    description="Delete an existing category. Requires admin or mediator role.",
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden - Insufficient privileges"},
        404: {"description": "Category not found"}
    },
    openapi_extra={
        "security": [{"Bearer": []}]
    }
)
async def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_privileged_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        repository = PostgresCategoryRepository(db)
        success = await repository.delete(category_id)
        if not success:
            raise NotFoundError("Category", category_id)
        return {"message": "Category deleted successfully"}
    except Exception as e:
        raise 