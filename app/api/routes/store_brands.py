from fastapi import APIRouter, Depends
from typing import List
from app.domain.models.store import StoreBrand
from app.domain.models.auth import User
from app.infrastructure.repositories.store.postgres_store_brand_repository import PostgresStoreBrandRepository
from app.api.dependencies.auth import get_current_privileged_user
from app.api.dependencies.services import get_store_brand_repository
from app.core.exceptions import NotFoundError
from app.infrastructure.logging.logger import get_logger
from app.api.responses.store import StoreBrandResponse
from app.api.models.store import StoreBrandRequest
from fastapi_cache.decorator import cache
from fastapi_cache import FastAPICache

logger = get_logger(__name__)

router = APIRouter(
    prefix="/store-brands",
    tags=["Store Brands"]
)

@router.post("/", 
    response_model=StoreBrand,
    summary="Create a new store brand",
    description="Create a new store brand. Requires admin or mediator role.",
    responses={
        401: {"description": "Unauthorized",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Authorization error",
                        "message": "Unauthorized to create a new store brand"
                    }
                }
            }},
        403: {"description": "Forbidden - Insufficient privileges",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Forbidden error",
                        "message": "Don't have permission to create a new store brand"
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
        "responses": {"422": None,}
    }
)
async def create_store_brand(
    store_brand: StoreBrandRequest,
    current_user: User = Depends(get_current_privileged_user),
    store_brand_repo: PostgresStoreBrandRepository = Depends(get_store_brand_repository)
):
    try:
        logger.info(f"Creating new store brand: {store_brand.name}")
        store_brand = await store_brand_repo.create(store_brand.name)
        logger.info(f"Created store brand with id: {store_brand.id}")
        await FastAPICache.clear(namespace="store_brands")
        await FastAPICache.clear(namespace="store_locations")
        await FastAPICache.clear(namespace="product_entries")
        return store_brand
    except Exception as e:
        logger.error(f"Error creating store brand: {str(e)}")
        raise

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
@cache(expire=3600, namespace="store_brands")
async def get_store_brand(
    store_brand_id: int,
    store_brand_repo: PostgresStoreBrandRepository = Depends(get_store_brand_repository)
):
    try:
        logger.info(f"Fetching store brand with id: {store_brand_id}")
        store_brand = await store_brand_repo.get(store_brand_id)
        if not store_brand:
            logger.warning(f"Store brand not found: {store_brand_id}")
            raise NotFoundError("Store brand", store_brand_id)
        return store_brand
    except Exception as e:
        logger.error(f"Error fetching store brand {store_brand_id}: {str(e)}")
        raise

@router.get("/", response_model=List[StoreBrandResponse])
@cache(expire=3600)
async def get_all_store_brands(
    store_brand_repo: PostgresStoreBrandRepository = Depends(get_store_brand_repository)
):
    logger.info("Fetching all store brands")
    return await store_brand_repo.get_all()

@router.put("/{store_brand_id}", 
    response_model=StoreBrand,
    summary="Update a store brand",
    description="Update an existing store brand. Requires admin or mediator role.",
    responses={
        401: {"description": "Unauthorized",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Authorization error",
                        "message": "Unauthorized to update a store brand"
                    }
                }
            }},
    }
)
async def update_store_brand(
    store_brand_id: int,
    name: str,
    current_user: User = Depends(get_current_privileged_user),
    store_brand_repo: PostgresStoreBrandRepository = Depends(get_store_brand_repository)
):
    try:
        logger.info(f"Updating store brand {store_brand_id} with name: {name}")
        store_brand = StoreBrand(id=store_brand_id, name=name)
        updated_brand = await store_brand_repo.update(store_brand_id, store_brand)
        if not updated_brand:
            logger.warning(f"Store brand not found for update: {store_brand_id}")
            raise NotFoundError("Store brand", store_brand_id)
        logger.info(f"Successfully updated store brand {store_brand_id}")
        await FastAPICache.clear(namespace="store_brands")
        await FastAPICache.clear(namespace="store_locations")
        await FastAPICache.clear(namespace="product_entries")
        return updated_brand
    except Exception as e:
        logger.error(f"Error updating store brand {store_brand_id}: {str(e)}")
        raise

@router.delete("/{store_brand_id}", 
    responses={
        401: {"description": "Unauthorized",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Authorization error",
                        "message": "Unauthorized to delete a store brand"
                    }
                }
            }},
    }
)
async def delete_store_brand(
    store_brand_id: int,
    current_user: User = Depends(get_current_privileged_user),
    store_brand_repo: PostgresStoreBrandRepository = Depends(get_store_brand_repository)
):
    try:
        logger.info(f"Attempting to delete store brand {store_brand_id}")
        success = await store_brand_repo.delete(store_brand_id)
        if not success:
            logger.warning(f"Store brand not found for deletion: {store_brand_id}")
            raise NotFoundError("Store brand", store_brand_id)
        logger.info(f"Successfully deleted store brand {store_brand_id}")
        await FastAPICache.clear(namespace="store_brands")
        await FastAPICache.clear(namespace="store_locations")
        await FastAPICache.clear(namespace="product_entries")
        return {"message": "Store brand deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting store brand {store_brand_id}: {str(e)}")
        raise 