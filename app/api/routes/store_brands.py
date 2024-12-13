from fastapi import APIRouter, Depends
from typing import List
from app.domain.models.auth import User
from app.api.dependencies.auth import get_current_privileged_user
from app.infrastructure.logging.logger import get_logger
from app.api.models.store import StoreBrandRequest
from app.api.responses.store import StoreBrandResponse
from fastapi_cache.decorator import cache
from app.core.config import settings
from app.core.container import Container
from app.services.store_brand_service import StoreBrandService
from dependency_injector.wiring import Provide, inject

logger = get_logger(__name__)

router = APIRouter(
    prefix="/store-brands",
    tags=["Store Brands"]
)

@router.post("/", 
    response_model=StoreBrandResponse,
    summary="Create a new store brand",
    description="Create a new store brand. Requires admin or mediator role.",
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
    store_brand_service: StoreBrandService = Depends(Provide[Container.store_brand_service])
):
    return await store_brand_service.create_store_brand(store_brand.name)

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
    store_brand_service: StoreBrandService = Depends(Provide[Container.store_brand_service])
):
    return await store_brand_service.get_store_brand(store_brand_id)

@router.get("/", response_model=List[StoreBrandResponse])
@cache(expire=settings.CACHE_TIME_LONG, namespace="store_brands")
@inject
async def get_all_store_brands(
    store_brand_service: StoreBrandService = Depends(Provide[Container.store_brand_service])
):
    return await store_brand_service.get_all_store_brands()


@router.put("/{store_brand_id}", 
    response_model=StoreBrandResponse,
    summary="Update a store brand",
    description="Update an existing store brand. Requires admin or mediator role.",
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
    store_brand_service: StoreBrandService = Depends(Provide[Container.store_brand_service])
):
    return await store_brand_service.update_store_brand(store_brand_id, store_brand.name)

@router.delete("/{store_brand_id}",
    summary="Delete a store brand",
    description="Delete an existing store brand. Requires admin or mediator role.",
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
    store_brand_service: StoreBrandService = Depends(Provide[Container.store_brand_service])
):
    await store_brand_service.delete_store_brand(store_brand_id)
    return {"message": "Store brand deleted successfully"} 