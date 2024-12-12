from fastapi import APIRouter, Depends
from typing import List
from app.domain.models.store import StoreLocation
from app.domain.models.auth import User
from app.infrastructure.repositories.store.postgres_store_location_repository import PostgresStoreLocationRepository
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.services import get_store_location_repository
from app.core.exceptions import NotFoundError
from app.infrastructure.logging.logger import get_logger
from app.api.responses.store import StoreLocationResponse, StoreLocationWithBrandResponse
from app.api.models.store import StoreLocationRequest

logger = get_logger(__name__)

router = APIRouter(
    prefix="/store-locations",
    tags=["Store Locations"]
)

@router.post("/", 
    response_model=StoreLocationResponse,
    summary="Create a new store location",
    description="Create a new store location. Requires authentication.",
    responses={
        401: {"description": "Unauthorized",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Authorization error",
                        "message": "Unauthorized to create a new store location"
                    }
                }
            }},
        403: {"description": "Forbidden",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Forbidden error",
                        "message": "Don't have permission to create a new store location"
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
        "responses": {"422": None,}
    }
)
async def create_store_location(
    location: StoreLocationRequest,
    current_user: User = Depends(get_current_user),
    location_repo: PostgresStoreLocationRepository = Depends(get_store_location_repository)
):
    try:
        logger.info(f"Creating new store location: Brand {location.store_brand_id}, Address {location.address}")
        location = await location_repo.create(location.store_brand_id, location.address)
        logger.info(f"Created store location with id: {location.id}")
        return location
    except ValueError as e:
        logger.warning(f"Invalid store brand id {location.store_brand_id}: {str(e)}")
        raise NotFoundError("Store brand", location.store_brand_id)
    except Exception as e:
        logger.error(f"Error creating store location: {str(e)}")
        raise

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
                    }}
            })
async def get_store_location(
    location_id: int,
    location_repo: PostgresStoreLocationRepository = Depends(get_store_location_repository)
):
    try:
        logger.info(f"Fetching store location with id: {location_id}")
        location = await location_repo.get(location_id)
        if not location:
            logger.warning(f"Store location not found: {location_id}")
            raise NotFoundError("Store location", location_id)
        return location
    except Exception as e:
        logger.error(f"Error fetching store location {location_id}: {str(e)}")
        raise

@router.get("/brand/{store_brand_id}", response_model=List[StoreLocation],
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
async def get_store_locations_by_brand(
    store_brand_id: int,
    location_repo: PostgresStoreLocationRepository = Depends(get_store_location_repository)
):
    try:
        logger.info(f"Fetching store locations for brand: {store_brand_id}")
        locations = await location_repo.get_by_store_brand(store_brand_id)
        logger.info(f"Found {len(locations)} locations for brand {store_brand_id}")
        return locations
    except Exception as e:
        logger.error(f"Error fetching locations for brand {store_brand_id}: {str(e)}")
        raise

@router.get("/", response_model=List[StoreLocationWithBrandResponse])
async def get_all_store_locations(
    location_repo: PostgresStoreLocationRepository = Depends(get_store_location_repository)
):
    logger.info("Fetching all store locations")
    return await location_repo.get_all()

@router.put("/{location_id}", 
    response_model=StoreLocation,
    summary="Update a store location",
    description="Update an existing store location. Requires authentication.",
    responses={
        401: {"description": "Unauthorized",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Authorization error",
                        "message": "Unauthorized to update a store location"
                    }
                }
            }},
        403: {"description": "Forbidden",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Forbidden error",
                        "message": "Don't have permission to update a store location"
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
        "responses": {"422": None,}
    }
)
async def update_store_location(
    location_id: int,
    address: str,
    current_user: User = Depends(get_current_user),
    location_repo: PostgresStoreLocationRepository = Depends(get_store_location_repository)
):
    try:
        logger.info(f"Updating store location {location_id} with address: {address}")
        store_location = StoreLocation(id=location_id, store_brand_id=0, address=address)
        updated_location = await location_repo.update(location_id, store_location)
        if not updated_location:
            logger.warning(f"Store location not found for update: {location_id}")
            raise NotFoundError("Store location", location_id)
        logger.info(f"Successfully updated store location {location_id}")
        return updated_location
    except Exception as e:
        logger.error(f"Error updating store location {location_id}: {str(e)}")
        raise

@router.delete("/{location_id}",
    summary="Delete a store location",
    description="Delete an existing store location. Requires authentication.",
    responses={
        401: {"description": "Unauthorized",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Authorization error",
                        "message": "Unauthorized to delete a store location"
                    }
                }
            }},
        403: {"description": "Forbidden",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Forbidden error",
                        "message": "Don't have permission to delete a store location"
                    }
                }
            }},
        404: {"description": "Not Found",
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
        "responses": {"422": None,}
    }
)
async def delete_store_location(
    location_id: int,
    current_user: User = Depends(get_current_user),
    location_repo: PostgresStoreLocationRepository = Depends(get_store_location_repository)
):
    try:
        logger.info(f"Attempting to delete store location {location_id}")
        success = await location_repo.delete(location_id)
        if not success:
            logger.warning(f"Store location not found for deletion: {location_id}")
            raise NotFoundError("Store location", location_id)
        logger.info(f"Successfully deleted store location {location_id}")
        return {"message": "Store location deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting store location {location_id}: {str(e)}")
        raise 