from fastapi import APIRouter, Depends, Query, HTTPException
from app.domain.models.auth import User
from app.api.dependencies.auth import get_current_privileged_user
from app.infrastructure.database.database import get_db
from app.infrastructure.logging.logger import get_logger
from app.api.responses.category import CategoryResponse, PaginatedCategoryResponse, SimpleCategoryResponse
from app.api.models.category import CategoryRequest
from fastapi_cache.decorator import cache
from app.core.config import settings
from app.core.container import Container
from app.services.category_service import CategoryService
from dependency_injector.wiring import Provide, inject
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

logger = get_logger(__name__)

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)

@router.post("/", 
    response_model=CategoryResponse,
    summary="Create a new category",
    description="Create a new category. Requires admin or moderator role.",
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

@router.get("/", 
    response_model=PaginatedCategoryResponse,
    summary="Get all categories",
    description="Get a paginated list of all categories with optional search and ordering."
)
@cache(expire=settings.CACHE_TIME_LONG, namespace="categories")
@inject
async def get_all_categories(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    search: str = Query(None, description="Search query for filtering categories by name"),
    order_by: str = Query("name", description="Field to order by (name, created_at)"),
    order_direction: str = Query("asc", description="Order direction (asc or desc)"),
    db: AsyncSession = Depends(get_db),
    category_service: CategoryService = Depends(Provide[Container.category_service])
) -> PaginatedCategoryResponse:
    """
    Get all categories with pagination and optional search.
    
    Args:
        page: Page number (default: 1)
        per_page: Number of items per page (default: 10, max: 100)
        search: Optional search query to filter categories by name
        order_by: Field to order by (default: name)
        order_direction: Order direction (asc or desc) (default: asc)
        db: Database session
        category_service: Category service instance
        
    Returns:
        PaginatedCategoryResponse containing the paginated list of categories
    """
    try:
        logger.info(f"Getting categories - page: {page}, per_page: {per_page}, search: {search}, order_by: {order_by}, order_direction: {order_direction}")
        return await category_service.get_all_categories(
            db=db,
            page=page,
            per_page=per_page,
            search=search,
            order_by=order_by,
            order_direction=order_direction
        )
    except Exception as e:
        logger.error(f"Error getting categories: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/simple", 
    response_model=List[SimpleCategoryResponse],
    summary="Get simplified categories list",
    description="Get a list of all categories with only ID and name. Useful for dropdowns and category selection.",
    responses={
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Server error",
                        "message": "An error occurred while retrieving categories"
                    }
                }
            }
        }
    }
)
@cache(expire=settings.CACHE_TIME_LONG, namespace="categories")
@inject
async def get_all_categories_simple(
    search: str = Query(None, description="Search query for filtering categories by name"),
    category_service: CategoryService = Depends(Provide[Container.category_service]),
    db: AsyncSession = Depends(get_db)
) -> List[SimpleCategoryResponse]:
    """
    Get a simplified list of all categories with optional search.
    
    Args:
        search: Optional search query to filter categories by name
        db: Database session
        category_service: Category service instance
        
    Returns:
        List of SimpleCategoryResponse containing only category IDs and names
    """
    try:
        logger.info(f"Getting simplified categories list - search: {search}")
        return await category_service.get_all_categories_simple(db, search=search)
    except Exception as e:
        logger.error(f"Error getting simplified categories list: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 

@router.put("/{category_id}", 
    response_model=CategoryResponse,
    summary="Update a category",
    description="Update an existing category. Requires admin or moderator role.",
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
    description="Delete an existing category. Requires admin or moderator role.",
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