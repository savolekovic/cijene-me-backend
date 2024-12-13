from fastapi import APIRouter, Depends
from typing import List
from decimal import Decimal
from app.domain.models.product import ProductEntry
from app.domain.models.auth import User
from app.api.dependencies.auth import get_current_privileged_user
from app.infrastructure.logging.logger import get_logger
from fastapi_cache.decorator import cache
from app.core.config import settings
from app.core.container import Container
from app.services.product_entry_service import ProductEntryService
from dependency_injector.wiring import Provide, inject

logger = get_logger(__name__)

router = APIRouter(
    prefix="/product-entries",
    tags=["Product Entries"]
)

@router.post("/", 
    response_model=ProductEntry,
    summary="Create a new price entry",
    description="Create a new price entry for a product. Requires admin or mediator role.",
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
    product_id: int,
    store_brand_id: int,
    store_location_id: int,
    price: Decimal,
    current_user: User = Depends(get_current_privileged_user),
    product_entry_service: ProductEntryService = Depends(Provide[Container.product_entry_service])
):
    return await product_entry_service.create_entry(
        product_id=product_id,
        store_brand_id=store_brand_id,
        store_location_id=store_location_id,
        price=price
    )

@router.get("/", response_model=List[ProductEntry])
@cache(expire=settings.CACHE_TIME_SHORT, namespace="product_entries")
@inject
async def get_all_product_entries(
    product_entry_service: ProductEntryService = Depends(Provide[Container.product_entry_service])
):
    return await product_entry_service.get_all_entries()

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
@cache(expire=settings.CACHE_TIME_SHORT)  # 5 minutes
@inject
async def get_product_entries_by_product(
    product_id: int,
    product_entry_service: ProductEntryService = Depends(Provide[Container.product_entry_service])
):
    return await product_entry_service.get_entries_by_product(product_id)

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
    product_entry_service: ProductEntryService = Depends(Provide[Container.product_entry_service])
):
    return await product_entry_service.get_entries_by_store_brand(store_brand_id)

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
@cache(expire=600, namespace="product_entries")
@inject
async def get_product_entries_by_store_location(
    store_location_id: int,
    product_entry_service: ProductEntryService = Depends(Provide[Container.product_entry_service])
):
     return await product_entry_service.get_entries_by_store_location(store_location_id)

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
    product_entry_service: ProductEntryService = Depends(Provide[Container.product_entry_service])
):
     return await product_entry_service.get_entry(entry_id=entry_id)