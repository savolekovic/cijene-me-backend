from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from app.domain.models.auth import User
from app.api.dependencies.auth import get_current_privileged_user
from app.infrastructure.logging.logger import get_logger
from app.api.models.store import StoreLocationRequest
from app.api.responses.store import StoreLocationResponse, StoreLocationResponse, PaginatedStoreLocationResponse, SimpleStoreLocationResponse
from fastapi_cache.decorator import cache
from app.core.config import settings
from app.core.container import Container
from app.services.store_location_service import StoreLocationService
from dependency_injector.wiring import Provide, inject
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.database import get_db

logger = get_logger(__name__)

router = APIRouter(
    prefix="/store-locations",
    tags=["Store Locations"]
)

@router.post("/", 
    response_model=StoreLocationResponse,
    summary="Create a new store location",
    description="Create a new store location. Requires admin or moderator role.",
    responses={
        401: {"description": "Unauthorized",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Authorization error",
                        "message": "Unauthorized to create store location"
                    }
                }
            }},
        403: {"description": "Forbidden",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Forbidden error",
                        "message": "Don't have permission to create store location"
                    }
                }
            }},
        409: {"description": "Conflict",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Conflict error",
                        "message": "Store location already exists"
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
async def create_store_location(
    store_location: StoreLocationRequest,
    current_user: User = Depends(get_current_privileged_user),
    store_location_service: StoreLocationService = Depends(Provide[Container.store_location_service]),
    db: AsyncSession = Depends(get_db)
):
    return await store_location_service.create_location(
        store_brand_id=store_location.store_brand_id,
        address=store_location.address,
        db=db
    )

@router.get("/simple", 
    response_model=List[SimpleStoreLocationResponse],
    summary="Get simplified store locations list",
    description="Get a list of all store locations with only essential information. Useful for dropdowns and location selection.",
    responses={
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Server error",
                        "message": "An error occurred while retrieving store locations"
                    }
                }
            }
        }
    }
)
@cache(expire=settings.CACHE_TIME_LONG, namespace="store_locations")
@inject
async def get_all_store_locations_simple(
    search: str = Query(None, description="Search query for filtering locations by address or store brand name"),
    store_brand_id: int = Query(None, description="Filter locations by store brand ID"),
    store_location_service: StoreLocationService = Depends(Provide[Container.store_location_service]),
    db: AsyncSession = Depends(get_db)
) -> List[SimpleStoreLocationResponse]:
    """
    Get a simplified list of all store locations with optional search and store brand filter.
    
    Args:
        search: Optional search query to filter locations by address or store brand name
        store_brand_id: Optional store brand ID to filter locations by specific brand
        db: Database session
        store_location_service: Store location service instance
        
    Returns:
        List of SimpleStoreLocationResponse containing only essential location information
    """
    try:
        logger.info(f"Getting simplified store locations list - search: {search}, store_brand_id: {store_brand_id}")
        return await store_location_service.get_all_store_locations_simple(
            db, 
            search=search,
            store_brand_id=store_brand_id
        )
    except Exception as e:
        logger.error(f"Error getting simplified store locations list: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=PaginatedStoreLocationResponse)
@cache(expire=settings.CACHE_TIME_LONG)
@inject
async def get_all_store_locations(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    search: str = Query(None, description="Search query for filtering locations by address or brand name"),
    order_by: str = Query("address", description="Field to order by (address, created_at, store_brand)"),
    order_direction: str = Query("asc", description="Order direction (asc or desc)"),
    db: AsyncSession = Depends(get_db),
    store_location_service: StoreLocationService = Depends(Provide[Container.store_location_service])
) -> PaginatedStoreLocationResponse:
    """
    Get all store locations with pagination, optional search, and ordering.
    
    Args:
        page: Page number (default: 1)
        per_page: Number of items per page (default: 10, max: 100)
        search: Optional search query to filter locations by address or brand name
        order_by: Field to order by (default: address)
        order_direction: Order direction (asc or desc) (default: asc)
        db: Database session
        store_location_service: Store location service instance
        
    Returns:
        PaginatedStoreLocationResponse containing the paginated list of store locations
    """
    try:
        logger.info(f"Getting store locations - page: {page}, per_page: {per_page}, search: {search}, order_by: {order_by}, order_direction: {order_direction}")
        return await store_location_service.get_all_store_locations(
            db=db,
            page=page,
            per_page=per_page,
            search=search,
            order_by=order_by,
            order_direction=order_direction
        )
    except Exception as e:
        logger.error(f"Error getting store locations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{location_id}", response_model=StoreLocationResponse,
            responses={
                404: {"description": "Not found",
                      "content": {
                        "application/json": {
                            "example": {
                                "error": "Not found error",
                                "message": "Store location not found"
                            }
                        }
                    }},
            })
@cache(expire=settings.CACHE_TIME_LONG, namespace="store_locations")
@inject
async def get_store_location(
    location_id: int,
    store_location_service: StoreLocationService = Depends(Provide[Container.store_location_service]),
    db: AsyncSession = Depends(get_db)
):
    return await store_location_service.get_location(location_id, db)

@router.get("/brand/{store_brand_id}", response_model=List[StoreLocationResponse],
            responses={
                404: {"description": "Not found",
                      "content": {
                        "application/json": {
                            "example": {
                                "error": "Not found error",
                                "message": "Store location not found"
                            }
                        }
                    }}
            })
@inject
async def get_store_locations_by_brand(
    store_brand_id: int,
    store_location_service: StoreLocationService = Depends(Provide[Container.store_location_service]),
    db: AsyncSession = Depends(get_db)
):
     return await store_location_service.get_store_locations_by_brand(store_brand_id=store_brand_id, db=db)

@router.put("/{location_id}", 
    response_model=StoreLocationResponse,
    summary="Update a store location",
    description="Update an existing store location. Requires admin or moderator role.",
    responses={
        401: {"description": "Unauthorized",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Authorization error",
                        "message": "Unauthorized to update store location"
                    }
                }
            }},
        403: {"description": "Forbidden",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Forbidden error",
                        "message": "Don't have permission to update store location"
                    }
                }
            }},
        404: {"description": "Not found",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Not found error",
                        "message": "Store location not found"
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
async def update_store_location(
    location_id: int,
    store_location: StoreLocationRequest,
    current_user: User = Depends(get_current_privileged_user),
    store_location_service: StoreLocationService = Depends(Provide[Container.store_location_service]),
    db: AsyncSession = Depends(get_db)
):
    return await store_location_service.update_location(
        location_id=location_id,
        store_brand_id=store_location.store_brand_id,
        address=store_location.address,
        db=db
    )

@router.delete("/{location_id}",
    summary="Delete a store location",
    description="Delete an existing store location. Requires admin or moderator role.",
    responses={
        401: {"description": "Unauthorized",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Authorization error",
                        "message": "Unauthorized to delete store location"
                    }
                }
            }},
        403: {"description": "Forbidden",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Forbidden error",
                        "message": "Don't have permission to delete store location"
                    }
                }
            }},
        404: {"description": "Not found",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Not found error",
                        "message": "Store location not found"
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
async def delete_store_location(
    location_id: int,
    current_user: User = Depends(get_current_privileged_user),
    store_location_service: StoreLocationService = Depends(Provide[Container.store_location_service]),
    db: AsyncSession = Depends(get_db)
):
    await store_location_service.delete_location(location_id, db)
    return {"message": "Store location deleted successfully"} 