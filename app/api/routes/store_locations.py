from fastapi import APIRouter, Depends
from typing import List
from app.domain.models.auth import User
from app.api.dependencies.auth import get_current_privileged_user
from app.domain.models.store.store_location import StoreLocation
from app.infrastructure.logging.logger import get_logger
from app.api.models.store import StoreLocationRequest
from app.api.responses.store import StoreLocationResponse, StoreLocationWithBrandResponse
from fastapi_cache.decorator import cache
from app.core.config import settings
from app.core.container import Container
from app.services.store_location_service import StoreLocationService
from dependency_injector.wiring import Provide, inject

logger = get_logger(__name__)

router = APIRouter(
    prefix="/store-locations",
    tags=["Store Locations"]
)

@router.post("/", 
    response_model=StoreLocationResponse,
    summary="Create a new store location",
    description="Create a new store location. Requires admin or mediator role.",
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
    store_location_service: StoreLocationService = Depends(Provide[Container.store_location_service])
):
    return await store_location_service.create_location(
        store_brand_id=store_location.store_brand_id,
        address=store_location.address
    )

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
    store_location_service: StoreLocationService = Depends(Provide[Container.store_location_service])
):
    return await store_location_service.get_location(location_id)

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
@inject
async def get_store_locations_by_brand(
    store_brand_id: int,
     store_location_service: StoreLocationService = Depends(Provide[Container.store_location_service])
):
     return await store_location_service.get_store_locations_by_brand(store_brand_id= store_brand_id)

@router.get("/", response_model=List[StoreLocationWithBrandResponse])
@cache(expire=settings.CACHE_TIME_LONG, namespace="store_locations")
@inject
async def get_all_store_locations(
    store_location_service: StoreLocationService = Depends(Provide[Container.store_location_service])
):
     return await store_location_service.get_all_locations()
   

@router.put("/{location_id}", 
    response_model=StoreLocationResponse,
    summary="Update a store location",
    description="Update an existing store location. Requires admin or mediator role.",
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
    store_location_service: StoreLocationService = Depends(Provide[Container.store_location_service])
):
    return await store_location_service.update_location(
        location_id=location_id,
        store_brand_id=store_location.store_brand_id,
        address=store_location.address
    )

@router.delete("/{location_id}",
    summary="Delete a store location",
    description="Delete an existing store location. Requires admin or mediator role.",
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
    store_location_service: StoreLocationService = Depends(Provide[Container.store_location_service])
):
    await store_location_service.delete_location(location_id)
    return {"message": "Store location deleted successfully"} 