from fastapi import APIRouter, Depends
from typing import List
from app.domain.models.auth import User
from app.api.dependencies.auth import get_current_privileged_user
from app.infrastructure.database.database import get_db
from app.infrastructure.logging.logger import get_logger
from app.api.responses.category import CategoryResponse
from app.api.models.category import CategoryRequest
from fastapi_cache.decorator import cache
from app.core.config import settings
from app.core.container import Container
from app.services.category_service import CategoryService
from dependency_injector.wiring import Provide, inject
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger(__name__)

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)

@router.post("/", 
    response_model=CategoryResponse,
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
@inject
async def create_category(
    category: CategoryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_privileged_user),
    category_service: CategoryService = Depends(Provide[Container.category_service])
):
    return await category_service.create_category(category.name, db)

@router.get("/", response_model=List[CategoryResponse])
@cache(expire=settings.CACHE_TIME_LONG, namespace="categories")
@inject
async def get_all_categories(
    db: AsyncSession = Depends(get_db),
    category_service: CategoryService = Depends(Provide[Container.category_service])
):
    return await category_service.get_all_categories(db)

@router.put("/{category_id}", 
    response_model=CategoryResponse,
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
@inject
async def update_category(
    category_id: int,
    category: CategoryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_privileged_user),
    category_service: CategoryService = Depends(Provide[Container.category_service])
):
    return await category_service.update_category(category_id, category.name, db)

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
@inject
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_privileged_user),
    category_service: CategoryService = Depends(Provide[Container.category_service])
):
    await category_service.delete_category(category_id, db)
    return {"message": "Category deleted successfully"}

@router.get("/{category_id}", 
    response_model=CategoryResponse,
    summary="Get category by ID",
    description="Get a specific category by ID. Public endpoint.",
    responses={
        404: {"description": "Not found",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Not found error",
                        "message": "Category not found"
                    }
                }
            }},
    }
)
@cache(expire=settings.CACHE_TIME_MEDIUM)
@inject
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    category_service: CategoryService = Depends(Provide[Container.category_service])
):
    return await category_service.get_category(category_id, db) 