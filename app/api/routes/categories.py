from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.api.models.category import CategoryRequest
from app.domain.models.product import Category
from app.domain.models.auth import User
from app.infrastructure.database.database import get_db
from app.infrastructure.repositories.product.postgres_category_repository import PostgresCategoryRepository
from app.api.dependencies.auth import get_current_privileged_user
from app.api.dependencies.services import get_category_repository
from app.core.exceptions import NotFoundError
from app.infrastructure.logging.logger import get_logger
from app.api.responses.category import CategoryResponse
from fastapi_cache.decorator import cache
from app.core.config import settings
from app.services.cache_service import CacheManager

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
        401: {"description": "Unauthorized",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Authorization error",
                        "message": "Unauthorized to create a category"
                    }
                }
            }},
        403: {"description": "Forbidden",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Forbidden error",
                        "message": "Don't have permission to create a category"
                    }
                }
            }},
        409: {"description": "Conflict",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Conflict error",
                        "message": "Category already exists"
                    }
                }
            }}
    },
    openapi_extra={
        "security": [{"Bearer": []}],
        "responses": {"422": None,}
    }

)
async def create_category(
    category: CategoryRequest,
    current_user: User = Depends(get_current_privileged_user),
    category_repo: PostgresCategoryRepository = Depends(get_category_repository)
):
    try:
        logger.info(f"Creating new category: {category.name}")
        new_category = await category_repo.create(name=category.name)
        logger.info(f"Created category with id: {new_category.id}")
        await CacheManager.clear_product_related_caches()
        return new_category
    except Exception as e:
        logger.error(f"Error creating category: {str(e)}")
        raise

@router.get("/", response_model=List[CategoryResponse])
@cache(expire=settings.CACHE_TIME_LONG, namespace="categories")  # 1 hour
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
         401: {"description": "Unauthorized",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Authorization error",
                        "message": "Unauthorized to update a category"
                    }
                }
            }},
        403: {"description": "Forbidden",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Forbidden error",
                        "message": "Don't have permission to update a category"
                    }
                }
            }},
        404: {"description": "Not found",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Not found error",
                        "message": "Category not found"
                    }
                }
            }},
    },
    openapi_extra={
        "security": [{"Bearer": []}],
        "responses": {"422": None,}
    }
)
async def update_category(
    category_id: int,
    category: CategoryRequest,
    current_user: User = Depends(get_current_privileged_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        repository = PostgresCategoryRepository(db)
        updated_category = await repository.update(category_id, Category(id=category_id, name=category.name))
        if not updated_category:
            raise NotFoundError("Category", category_id)
        await CacheManager.clear_product_related_caches()
        return updated_category
    except Exception as e:
        raise

@router.delete("/{category_id}",
    summary="Delete a category",
    description="Delete an existing category. Requires admin or mediator role.",
    responses={
        401: {"description": "Unauthorized",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Authorization error",
                        "message": "Unauthorized to delete a category"
                    }
                }
            }},
        403: {"description": "Forbidden",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Forbidden error",
                        "message": "Don't have permission to delete a category"
                    }
                }
            }},
        404: {"description": "Not found",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Not found error",
                        "message": "Category not found"
                    }
                }
            }},
    },
    openapi_extra={
        "security": [{"Bearer": []}],
        "responses": {"422": None,}
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
        await CacheManager.clear_product_related_caches()
        return {"message": "Category deleted successfully"}
    except Exception as e:
        raise 