from fastapi import APIRouter, Depends, UploadFile, File, Form
from typing import List
from app.domain.models.product import Product
from app.domain.models.auth import User
from app.infrastructure.database.database import get_db
from app.api.dependencies.auth import get_current_privileged_user
from app.infrastructure.logging.logger import get_logger
from app.api.responses.product import ProductWithCategoryResponse, PaginatedProductResponse
from app.api.models.product import ProductRequest
from fastapi_cache.decorator import cache
from app.core.config import settings
from app.core.container import Container
from app.services.product_service import ProductService
from dependency_injector.wiring import Provide, inject
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.utils.file_upload import save_upload_file, delete_upload_file
from fastapi.openapi.models import MediaType

logger = get_logger(__name__)

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

@router.post("/", 
    response_model=Product,
    summary="Create a new product",
    description="Create a new product with image upload. Requires admin or moderator role.",
    responses={
        200: {
            "description": "Successfully created product",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "name": "Jagodica",
                        "barcode": "12345670",
                        "image_url": "/static/uploads/product_1.jpg",
                        "category_id": 4,
                        "created_at": "2024-01-20T12:00:00"
                    }
                }
            }
        },
        401: {
            "description": "Unauthorized",
            "content": {
                "application/json": {
                    "example": {"detail": "Not authenticated"}
                }
            }
        },
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "Not enough privileges"}
                }
            }
        }
    },
    openapi_extra={
        "security": [{"Bearer": []}],
        "requestBody": {
            "content": {
                "multipart/form-data": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "example": "Jagodica"
                            },
                            "barcode": {
                                "type": "string",
                                "example": "12345670"
                            },
                            "category_id": {
                                "type": "integer",
                                "example": 4
                            },
                            "image": {
                                "type": "string",
                                "format": "binary",
                                "description": "Product image file (JPEG, PNG, or GIF)"
                            }
                        },
                        "required": ["name", "barcode", "category_id", "image"]
                    }
                }
            }
        }
    }
)
@inject
async def create_product(
    name: str = Form(
        ...,
        description="Product name",
        example="Jagodica"
    ),
    barcode: str = Form(
        ...,
        description="Product barcode",
        example="12345670"
    ),
    category_id: int = Form(
        ...,
        description="Category ID",
        example=4
    ),
    image: UploadFile = File(
        ...,
        description="Product image (JPEG, PNG, or GIF)"
    ),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_privileged_user),
    product_service: ProductService = Depends(Provide[Container.product_service])
):
    logger.info(f"Received product creation request:")
    logger.info(f"Name: {name}")
    logger.info(f"Barcode: {barcode}")
    logger.info(f"Category ID: {category_id}")
    logger.info(f"Image filename: {image.filename}")
    logger.info(f"Headers: {image.headers}")  # This might help identify auth header issues
    
    # Save uploaded image
    image_path = await save_upload_file(image)
    
    return await product_service.create_product(
        name=name,
        barcode=barcode,
        image_url=image_path,
        category_id=category_id,
        db=db
    )

@router.get("/", response_model=PaginatedProductResponse)
@cache(expire=settings.CACHE_TIME_LONG)
@inject
async def get_all_products(
    page: int = 1,
    per_page: int = 10,
    search: str = None,
    product_service: ProductService = Depends(Provide[Container.product_service]),
    db: AsyncSession = Depends(get_db)
):
    return await product_service.get_all_products(db, page=page, per_page=per_page, search=search)

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
@cache(expire=settings.CACHE_TIME_MEDIUM)
@inject
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    product_service: ProductService = Depends(Provide[Container.product_service])
):
    return await product_service.get_product(product_id, db)

@router.put("/{product_id}", 
    response_model=Product,
    summary="Update a product",
    description="Update an existing product. Requires admin or moderator role.",
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
@inject
async def update_product(
    product_id: int,
    product: ProductRequest,
    image: UploadFile | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_privileged_user),
    product_service: ProductService = Depends(Provide[Container.product_service])
):
    # Get existing product to handle image update
    existing_product = await product_service.get_product(product_id, db)
    
    # Handle image update
    image_path = existing_product.image_url
    if image:
        # Delete old image if it exists
        await delete_upload_file(existing_product.image_url)
        # Save new image
        image_path = await save_upload_file(image)
    
    return await product_service.update_product(
        product_id=product_id,
        name=product.name,
        image_url=image_path,
        category_id=product.category_id,
        db=db
    )

@router.delete("/{product_id}",
    summary="Delete a product",
    description="Delete an existing product. Requires admin or moderator role.",
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
@inject
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_privileged_user),
    product_service: ProductService = Depends(Provide[Container.product_service])
):
    # Get product to delete its image
    product = await product_service.get_product(product_id, db)
    
    # Delete the product's image
    await delete_upload_file(product.image_url)
    
    # Delete the product
    await product_service.delete_product(product_id, db)