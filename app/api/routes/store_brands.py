from fastapi import APIRouter, Depends, HTTPException, Query
from app.domain.models.auth import User
from app.api.dependencies.auth import get_current_privileged_user
from app.infrastructure.logging.logger import get_logger
from app.api.models.store import StoreBrandRequest
from app.api.responses.store import StoreBrandResponse, PaginatedStoreBrandResponse
from fastapi_cache.decorator import cache
from app.core.config import settings
from app.core.container import Container
from app.services.store_brand_service import StoreBrandService
from dependency_injector.wiring import Provide, inject
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.database import get_db

logger = get_logger(__name__)

router = APIRouter(
    prefix="/store-brands",
    tags=["Store Brands"]
)

@router.post("/", 
    response_model=StoreBrandResponse,
    summary="Create a new store brand",
    description="Create a new store brand. Requires admin or moderator role.",
    responses={
        401: {"description": "Unauthorized",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Authorization error",
                        "message": "Unauthorized to create store brand"
                    }
                }
            }},
        403: {"description": "Forbidden",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Forbidden error",
                        "message": "Don't have permission to create store brand"
                    }
                }
            }},
        409: {"description": "Conflict",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Conflict error",
                        "message": "Store brand already exists"
                    }
                }
            }}
    },
    openapi_extra={
        "security": [{"Bearer": []}],
        "responses": {"422": None}
    }
)
@inject
async def create_store_brand(
    store_brand: StoreBrandRequest,
    current_user: User = Depends(get_current_privileged_user),
    store_brand_service: StoreBrandService = Depends(Provide[Container.store_brand_service]),
    db: AsyncSession = Depends(get_db)
):
    return await store_brand_service.create_store_brand(store_brand.name, db)

@router.get("/{store_brand_id}", response_model=StoreBrandResponse,
            responses={
                404: {"description": "Not found",
                      "content": {
                        "application/json": {
                            "example": {
                                "error": "Not found error",
                                "message": "Store brand not found"
                            }
                        }
                    }},
            })
@cache(expire=settings.CACHE_TIME_LONG, namespace="store_brands")
@inject
async def get_store_brand(
    store_brand_id: int,
    store_brand_service: StoreBrandService = Depends(Provide[Container.store_brand_service]),
    db: AsyncSession = Depends(get_db)
):
    return await store_brand_service.get_store_brand(store_brand_id, db)

@router.get("/", response_model=PaginatedStoreBrandResponse)
@cache(expire=settings.CACHE_TIME_LONG)
@inject
async def get_all_store_brands(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    search: str = Query(None, description="Search query for filtering brands by name"),
    db: AsyncSession = Depends(get_db),
    store_brand_service: StoreBrandService = Depends(Provide[Container.store_brand_service])
) -> PaginatedStoreBrandResponse:
    """
    Get all store brands with pagination and optional search.
    
    Args:
        page: Page number (default: 1)
        per_page: Number of items per page (default: 10, max: 100)
        search: Optional search query to filter brands by name
        db: Database session
        store_brand_service: Store brand service instance
        
    Returns:
        PaginatedStoreBrandResponse containing the paginated list of store brands
    """
    try:
        logger.info(f"Getting store brands - page: {page}, per_page: {per_page}, search: {search}")
        return await store_brand_service.get_all_store_brands(
            db=db,
            page=page,
            per_page=per_page,
            search=search
        )
    except Exception as e:
        logger.error(f"Error getting store brands: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{store_brand_id}", 
    response_model=StoreBrandResponse,
    summary="Update a store brand",
    description="Update an existing store brand. Requires admin or moderator role.",
    responses={
        401: {"description": "Unauthorized",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Authorization error",
                        "message": "Unauthorized to update store brand"
                    }
                }
            }},
        403: {"description": "Forbidden",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Forbidden error",
                        "message": "Don't have permission to update store brand"
                    }
                }
            }},
        404: {"description": "Not found",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Not found error",
                        "message": "Store brand not found"
                    }
                }
            }}
    },
    openapi_extra={
        "security": [{"Bearer": []}],
        "responses": {"422": None}
    }
)
@inject
async def update_store_brand(
    store_brand_id: int,
    store_brand: StoreBrandRequest,
    current_user: User = Depends(get_current_privileged_user),
    store_brand_service: StoreBrandService = Depends(Provide[Container.store_brand_service]),
    db: AsyncSession = Depends(get_db)
):
    return await store_brand_service.update_store_brand(store_brand_id, store_brand.name, db)

@router.delete("/{store_brand_id}",
    summary="Delete a store brand",
    description="Delete an existing store brand. Requires admin or moderator role.",
    responses={
        401: {"description": "Unauthorized",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Authorization error",
                        "message": "Unauthorized to delete store brand"
                    }
                }
            }},
        403: {"description": "Forbidden",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Forbidden error",
                        "message": "Don't have permission to delete store brand"
                    }
                }
            }},
        404: {"description": "Not found",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Not found error",
                        "message": "Store brand not found"
                    }
                }
            }}
    },
    openapi_extra={
        "security": [{"Bearer": []}],
        "responses": {"422": None}
    }
)
@inject
async def delete_store_brand(
    store_brand_id: int,
    current_user: User = Depends(get_current_privileged_user),
    store_brand_service: StoreBrandService = Depends(Provide[Container.store_brand_service]),
    db: AsyncSession = Depends(get_db)
):
    await store_brand_service.delete_store_brand(store_brand_id, db)
    return {"message": "Store brand deleted successfully"} 