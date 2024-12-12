from fastapi import APIRouter, Depends
from typing import List
from app.core.exceptions import NotFoundError
from app.domain.models.product import Product
from app.domain.models.auth import User
from app.infrastructure.repositories.product.postgres_product_repository import PostgresProductRepository
from app.api.dependencies.auth import get_current_privileged_user
from app.api.dependencies.services import get_product_repository
from app.infrastructure.logging.logger import get_logger
from app.api.responses.product import ProductWithCategoryResponse
from app.api.models.product import ProductRequest
from fastapi_cache.decorator import cache
from app.core.config import settings
from app.services.cache_service import CacheManager

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
        401: {"description": "Unauthorized",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Authorization error",
                        "message": "Unauthorized to create a new product"
                    }
                }
            }},
        403: {"description": "Forbidden",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Forbidden error",
                        "message": "Don't have permission to create a new product"
                    }
                }
            }},
        409: {"description": "Conflict",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Conflict error",
                        "message": "Product already exists"
                    }
                }
            }}
    },
    openapi_extra={
        "security": [{"Bearer": []}],
        "responses": {"422": None,}
    }
)
async def create_product(
    product: ProductRequest,
    current_user: User = Depends(get_current_privileged_user),
    product_repo: PostgresProductRepository = Depends(get_product_repository)
):
    try:
        logger.info(f"Creating new product: {product.name} in category {product.category_id}")
        product = await product_repo.create(
            name=product.name,
            image_url=product.image_url,
            category_id=product.category_id
        )
        logger.info(f"Created product with id: {product.id}")
        await CacheManager.clear_product_related_caches()
        return product
    except Exception as e:
        logger.error(f"Error creating product: {str(e)}")
        raise

@router.get("/", response_model=List[ProductWithCategoryResponse])
@cache(expire=settings.CACHE_TIME_MEDIUM)  # 30 minutes
async def get_all_products(
    product_repo: PostgresProductRepository = Depends(get_product_repository)
):
    logger.info("Fetching all products with categories")
    return await product_repo.get_all_with_categories()

@router.get("/{product_id}", response_model=Product,
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
@cache(expire=settings.CACHE_TIME_MEDIUM)  # 30 minutes
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
        401: {"description": "Unauthorized",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Authorization error",
                        "message": "Unauthorized to update a product"
                    }
                }
            }},
        403: {"description": "Forbidden",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Forbidden error",
                        "message": "Don't have permission to update a product"
                    }
                }
            }},
        404: {"description": "Not found",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Not found error",
                        "message": "Product not found"
                    }
                }
            }},
    },
    openapi_extra={
        "security": [{"Bearer": []}],
        "responses": {"422": None,}
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
        await CacheManager.clear_product_related_caches()
        return updated_product
    except Exception as e:
        logger.error(f"Error updating product {product_id}: {str(e)}")
        raise

@router.delete("/{product_id}",
    summary="Delete a product",
    description="Delete an existing product. Requires admin or mediator role.",
    responses={
        401: {"description": "Unauthorized",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Authorization error",
                        "message": "Unauthorized to delete a product"
                    }
                }
            }},
        403: {"description": "Forbidden",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Forbidden error",
                        "message": "Don't have permission to delete a product"
                    }
                }
            }},
        404: {"description": "Not found",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Not found error",
                        "message": "Product not found"
                    }
                }
            }},
    },
    openapi_extra={
        "security": [{"Bearer": []}],
        "responses": {"422": None,}
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
        await CacheManager.clear_product_related_caches()
        return {"message": "Product deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting product {product_id}: {str(e)}")
        raise 