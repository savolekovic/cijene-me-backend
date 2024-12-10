from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.exceptions import NotFoundError
from app.domain.models.product import Product, ProductWithCategory
from app.domain.models.auth import User
from app.infrastructure.database.database import get_db
from app.infrastructure.repositories.product.postgres_product_repository import PostgresProductRepository
from app.api.dependencies.auth import get_current_privileged_user
from app.api.dependencies.services import get_product_repository
from app.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)

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
        403: {"description": "Forbidden"}
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
    product_repo: PostgresProductRepository = Depends(get_product_repository)
):
    try:
        logger.info(f"Creating new product: {name} in category {category_id}")
        product = await product_repo.create(
            name=name,
            image_url=image_url,
            category_id=category_id
        )
        logger.info(f"Created product with id: {product.id}")
        return product
    except Exception as e:
        logger.error(f"Error creating product: {str(e)}")
        raise

@router.get("/", response_model=List[ProductWithCategory])
async def get_all_products(
    product_repo: PostgresProductRepository = Depends(get_product_repository)
):
    logger.info("Fetching all products with categories")
    return await product_repo.get_all_with_categories()

@router.get("/{product_id}", response_model=Product)
async def get_product(
    product_id: int,
    product_repo: PostgresProductRepository = Depends(get_product_repository)
):
    try:
        logger.info(f"Fetching product with id: {product_id}")
        product = await product_repo.get(product_id)
        if not product:
            logger.warning(f"Product not found: {product_id}")
            raise NotFoundError("Product", product_id)
        return product
    except Exception as e:
        logger.error(f"Error fetching product {product_id}: {str(e)}")
        raise

@router.put("/{product_id}", 
    response_model=Product,
    summary="Update a product",
    description="Update an existing product. Requires admin or mediator role.",
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Not found"}
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
    product_repo: PostgresProductRepository = Depends(get_product_repository)
):
    try:
        logger.info(f"Updating product {product_id} with name: {name}")
        product = Product(
            id=product_id,
            name=name,
            image_url=image_url,
            category_id=category_id
        )
        updated_product = await product_repo.update(product_id, product)
        if not updated_product:
            logger.warning(f"Product not found for update: {product_id}")
            raise NotFoundError("Product", product_id)
        logger.info(f"Successfully updated product {product_id}")
        return updated_product
    except Exception as e:
        logger.error(f"Error updating product {product_id}: {str(e)}")
        raise

@router.delete("/{product_id}",
    summary="Delete a product",
    description="Delete an existing product. Requires admin or mediator role.",
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Not found"}
    },
    openapi_extra={
        "security": [{"Bearer": []}]
    }
)
async def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_privileged_user),
    product_repo: PostgresProductRepository = Depends(get_product_repository)
):
    try:
        logger.info(f"Attempting to delete product {product_id}")
        success = await product_repo.delete(product_id)
        if not success:
            logger.warning(f"Product not found for deletion: {product_id}")
            raise NotFoundError("Product", product_id)
        logger.info(f"Successfully deleted product {product_id}")
        return {"message": "Product deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting product {product_id}: {str(e)}")
        raise 