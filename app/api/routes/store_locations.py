from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging
from app.domain.models.store_location import StoreLocation
from app.domain.models.user import User
from app.infrastructure.database.database import get_db
from app.infrastructure.repositories.postgres_store_location_repository import PostgresStoreLocationRepository
from app.api.dependencies.auth import get_current_user

router = APIRouter(
    prefix="/store-locations",
    tags=["Store Locations"]
)

# Common response definition
unauthorized_response = {
    401: {
        "description": "Unauthorized - Invalid or missing authentication token",
        "content": {
            "application/json": {
                "example": {"detail": "Could not validate credentials"}
            }
        }
    }
}

@router.post("/", 
    response_model=StoreLocation,
    summary="Create a new store location",
    description="Create a new store location. Requires authentication.",
    responses=unauthorized_response,
    openapi_extra={
        "security": [{"Bearer": []}]
    }
)
async def create_store_location(
    store_brand_id: int,
    address: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        repository = PostgresStoreLocationRepository(db)
        return await repository.create(store_brand_id, address)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logging.error(f"Error creating store location: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{location_id}", response_model=StoreLocation)
async def get_store_location(
    location_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        repository = PostgresStoreLocationRepository(db)
        location = await repository.get(location_id)
        if not location:
            raise HTTPException(status_code=404, detail="Store location not found")
        return location
    except Exception as e:
        logging.error(f"Error getting store location: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/brand/{store_brand_id}", response_model=List[StoreLocation])
async def get_store_locations_by_brand(
    store_brand_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        repository = PostgresStoreLocationRepository(db)
        return await repository.get_by_store_brand(store_brand_id)
    except Exception as e:
        logging.error(f"Error getting store locations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[StoreLocation])
async def get_all_store_locations(
    db: AsyncSession = Depends(get_db)
):
    try:
        repository = PostgresStoreLocationRepository(db)
        return await repository.get_all()
    except Exception as e:
        logging.error(f"Error getting all store locations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{location_id}", 
    response_model=StoreLocation,
    summary="Update a store location",
    description="Update an existing store location. Requires authentication.",
    responses=unauthorized_response,
    openapi_extra={
        "security": [{"Bearer": []}]
    }
)
async def update_store_location(
    location_id: int,
    address: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        repository = PostgresStoreLocationRepository(db)
        store_location = StoreLocation(id=location_id, store_brand_id=0, address=address)
        updated_location = await repository.update(location_id, store_location)
        if not updated_location:
            raise HTTPException(status_code=404, detail="Store location not found")
        return updated_location
    except Exception as e:
        logging.error(f"Error updating store location: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{location_id}",
    summary="Delete a store location",
    description="Delete an existing store location. Requires authentication.",
    responses=unauthorized_response,
    openapi_extra={
        "security": [{"Bearer": []}]
    }
)
async def delete_store_location(
    location_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        repository = PostgresStoreLocationRepository(db)
        success = await repository.delete(location_id)
        if not success:
            raise HTTPException(status_code=404, detail="Store location not found")
        return {"message": "Store location deleted successfully"}
    except Exception as e:
        logging.error(f"Error deleting store location: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 