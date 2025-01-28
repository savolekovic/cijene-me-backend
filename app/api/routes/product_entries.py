from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from app.api.models.product_entry import ProductEntryRequest
from app.domain.models.product import ProductEntry
from app.domain.models.auth import User
from app.api.dependencies.auth import get_current_privileged_user
from app.infrastructure.logging.logger import get_logger
from fastapi_cache.decorator import cache
from app.core.config import settings
from app.core.container import Container
from app.services.product_entry_service import ProductEntryService
from dependency_injector.wiring import Provide, inject
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.database import get_db
from app.api.responses.product_entry import ProductEntryWithDetails, PaginatedProductEntryResponse
from datetime import datetime

logger = get_logger(__name__)

router = APIRouter(
    prefix="/product-entries",
    tags=["Product Entries"]
)

@router.post("/", 
    response_model=ProductEntryWithDetails,
    summary="Create a new price entry",
    description="Create a new price entry for a product. Requires admin or moderator role.",
    responses={
        401: {"description": "Unauthorized",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Authorization error",
                        "message": "Unauthorized to create a product entry"
                    }
                }
            }},
        403: {"description": "Forbidden",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Forbidden error",
                        "message": "Don't have permission to create a product entry"
                    }
                }
            }},
        409: {"description": "Conflict",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Conflict error",
                        "message": "Product entry already exists"
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
async def create_product_entry(
    entry: ProductEntryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_privileged_user),
    product_entry_service: ProductEntryService = Depends(Provide[Container.product_entry_service])
):
    return await product_entry_service.create_product_entry(
        product_id=entry.product_id,
        store_location_id=entry.store_location_id,
        price=entry.price,
        db=db
    )

@router.get("/", response_model=PaginatedProductEntryResponse)
@cache(expire=settings.CACHE_TIME_LONG, namespace="product_entries")
@inject
async def get_all_product_entries(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    search: str = Query(None, description="Search query for filtering entries"),
    product_id: int = Query(None, description="Filter entries by product ID"),
    store_brand_id: int = Query(None, description="Filter entries by store brand ID"),
    store_location_id: int = Query(None, description="Filter entries by store location ID"),
    min_price: float = Query(None, ge=0, description="Minimum price filter"),
    max_price: float = Query(None, ge=0, description="Maximum price filter"),
    from_date: datetime = Query(None, description="Filter entries from this date"),
    to_date: datetime = Query(None, description="Filter entries until this date"),
    order_by: str = Query("created_at", description="Field to order by (created_at, price)"),
    order_direction: str = Query("desc", description="Order direction (asc or desc)"),
    db: AsyncSession = Depends(get_db),
    product_entry_service: ProductEntryService = Depends(Provide[Container.product_entry_service])
) -> PaginatedProductEntryResponse:
    """
    Get all product entries with pagination and filtering options.
    
    Args:
        page: Page number (default: 1)
        per_page: Number of items per page (default: 10, max: 100)
        search: Optional search query to filter entries
        product_id: Optional product ID to filter entries
        store_brand_id: Optional store brand ID to filter entries
        store_location_id: Optional store location ID to filter entries
        min_price: Optional minimum price filter
        max_price: Optional maximum price filter
        from_date: Optional start date filter
        to_date: Optional end date filter
        order_by: Field to order by (default: created_at)
        order_direction: Order direction (asc or desc) (default: desc)
        db: Database session
        product_entry_service: Product entry service instance
        
    Returns:
        PaginatedProductEntryResponse containing the filtered and paginated list of product entries
    """
    try:
        logger.info(f"Getting product entries - page: {page}, per_page: {per_page}, search: {search}, " +
                   f"product_id: {product_id}, store_brand_id: {store_brand_id}, " +
                   f"store_location_id: {store_location_id}, min_price: {min_price}, " +
                   f"max_price: {max_price}, from_date: {from_date}, to_date: {to_date}, " +
                   f"order_by: {order_by}, order_direction: {order_direction}")
        
        return await product_entry_service.get_all_product_entries(
            db=db,
            page=page,
            per_page=per_page,
            search=search,
            product_id=product_id,
            store_brand_id=store_brand_id,
            store_location_id=store_location_id,
            min_price=min_price,
            max_price=max_price,
            from_date=from_date,
            to_date=to_date,
            order_by=order_by,
            order_direction=order_direction
        )
    except Exception as e:
        logger.error(f"Error getting product entries: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/product/{product_id}", response_model=List[ProductEntry],
            responses={
                404: {"description": "Not found",
                      "content": {
                        "application/json": {
                            "example": {
                                "error": "Not found error",
                                "message": "Product not found"
                            }
                        }
                    }},
            })
@cache(expire=settings.CACHE_TIME_SHORT, namespace="product_entries")
@inject
async def get_product_entries_by_product(
    product_id: int,
    product_entry_service: ProductEntryService = Depends(Provide[Container.product_entry_service]),
    db: AsyncSession = Depends(get_db)
):
    return await product_entry_service.get_entries_by_product(product_id, db)

@router.get("/store-brand/{store_brand_id}", response_model=List[ProductEntry],
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
@cache(expire=settings.CACHE_TIME_SHORT, namespace="product_entries")
@inject
async def get_product_entries_by_store_brand(
    store_brand_id: int,
    product_entry_service: ProductEntryService = Depends(Provide[Container.product_entry_service]),
    db: AsyncSession = Depends(get_db)
):
    return await product_entry_service.get_entries_by_store_brand(store_brand_id, db)

@router.get("/store-location/{store_location_id}", response_model=List[ProductEntry],
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
@cache(expire=settings.CACHE_TIME_SHORT, namespace="product_entries")
@inject
async def get_product_entries_by_store_location(
    store_location_id: int,
    product_entry_service: ProductEntryService = Depends(Provide[Container.product_entry_service]),
    db: AsyncSession = Depends(get_db)
):
     return await product_entry_service.get_entries_by_store_location(store_location_id, db)

@router.get("/{entry_id}", response_model=ProductEntry,
            responses={
                404: {"description": "Not found",
                      "content": {
                        "application/json": {
                            "example": {
                                "error": "Not found error",
                                "message": "Product entry not found"
                            }
                        }
                    }},
            })
@inject
async def get_product_entry(
    entry_id: int,
    product_entry_service: ProductEntryService = Depends(Provide[Container.product_entry_service]),
    db: AsyncSession = Depends(get_db)
):
     return await product_entry_service.get_entry(entry_id=entry_id, db=db)

@router.delete("/{entry_id}",
    summary="Delete a product entry",
    description="Delete an existing product entry. Requires admin or moderator role.",
    responses={
        401: {"description": "Unauthorized",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Authorization error",
                        "message": "Unauthorized to delete a product entry"
                    }
                }
            }},
        403: {"description": "Forbidden",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Forbidden error",
                        "message": "Don't have permission to delete a product entry"
                    }
                }
            }},
        404: {"description": "Not found",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Not found error",
                        "message": "Product entry not found"
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
async def delete_product_entry(
    entry_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_privileged_user),
    product_entry_service: ProductEntryService = Depends(Provide[Container.product_entry_service])
):
    await product_entry_service.delete_entry(entry_id, db)
    return {"message": "Product entry deleted successfully"}
