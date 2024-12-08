from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.exceptions import NotFoundError
from app.domain.models.product import Product, ProductWithCategory
from app.domain.models.auth import User
from app.infrastructure.database.database import get_db
from app.infrastructure.repositories.product.postgres_product_repository import PostgresProductRepository
from app.api.dependencies.auth import get_current_privileged_user

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

@router.post("/", 
    response_model=Product,
    summary="Create a new product",
    description="Create a new product. Requires admin or mediator role.",
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden - Insufficient privileges"}
    },
    openapi_extra={
        "security": [{"Bearer": []}]
    }
)
async def create_product(
    name: str,
    image_url: str,
    category_id: int,
    current_user: User = Depends(get_current_privileged_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        repository = PostgresProductRepository(db)
        return await repository.create(
            name=name,
            image_url=image_url,
            category_id=category_id
        )
    except Exception as e:
        raise

@router.get("/", response_model=List[ProductWithCategory])
async def get_all_products(
    db: AsyncSession = Depends(get_db)
):
    repository = PostgresProductRepository(db)
    return await repository.get_all_with_categories()

@router.get("/{product_id}", response_model=Product)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        repository = PostgresProductRepository(db)
        return await repository.get(product_id)
    except Exception as e:
        raise 

@router.put("/{product_id}", 
    response_model=Product,
    summary="Update a product",
    description="Update an existing product. Requires admin or mediator role.",
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden - Insufficient privileges"},
        404: {"description": "Product not found"}
    },
    openapi_extra={
        "security": [{"Bearer": []}]
    }
)
async def update_product(
    product_id: int,
    name: str,
    image_url: str,
    category_id: int,
    current_user: User = Depends(get_current_privileged_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        repository = PostgresProductRepository(db)
        product = Product(
            id=product_id,
            name=name,
            image_url=image_url,
            category_id=category_id
        )
        updated_product = await repository.update(product_id, product)
        if not updated_product:
            raise NotFoundError("Product", product_id)
        return updated_product
    except Exception as e:
        raise

@router.delete("/{product_id}",
    summary="Delete a product",
    description="Delete an existing product. Requires admin or mediator role.",
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden - Insufficient privileges"},
        404: {"description": "Product not found"}
    },
    openapi_extra={
        "security": [{"Bearer": []}]
    }
)
async def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_privileged_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        repository = PostgresProductRepository(db)
        success = await repository.delete(product_id)
        if not success:
            raise NotFoundError("Product", product_id)
        return {"message": "Product deleted successfully"}
    except Exception as e:
        raise 