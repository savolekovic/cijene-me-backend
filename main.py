from fastapi import FastAPI, Request, status
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.exceptions import RequestValidationError
import logging
from app.api.routes import (
    store_brands,
    store_locations,
    auth,
    users,
    categories,
    products,
    product_entries
)
from app.core.exceptions import DatabaseError, NotFoundError, ValidationError, AuthenticationError

app = FastAPI(
    responses={
        422: {
            "description": "Validation Error",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Validation error",
                        "message": "Enter a valid email address."
                    },
                    "schema": {
                        "type": "object",
                        "properties": {
                            "error": {
                                "type": "string",
                                "example": "Validation error"
                            },
                            "message": {
                                "type": "string",
                                "example": "Enter a valid email address."
                            }
                        }
                    }
                }
            }
        }
    }
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Cijene.me API",
        version="1.0.0",
        description="Odje treba napisati opis API-ja",
        routes=app.routes,
    )
    
    # Add JWT bearer security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter JWT Bearer token"
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Auth routes
app.include_router(auth.router)

# User management routes
app.include_router(users.router)

# Store management routes
app.include_router(store_brands.router)
app.include_router(store_locations.router)

# Product management routes
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(product_entries.router)

# Add custom exception handler for form validation
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    
    # When no body is provided
    if any(error["type"] == "missing" for error in errors):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "Validation error",
                "message": "Request body is required"
            }
        )
    
    # When email format is invalid
    if any(error["type"] == "value_error.email" for error in errors):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "Validation error",
                "message": "Enter a valid email address."
            }
        )
    
    # When grant_type is missing or invalid
    if any(error["loc"][1] == "grant_type" for error in errors):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "Validation error",
                "message": "Invalid login request"
            }
        )
    
    # For any other validation errors
    error = errors[0]
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Validation error",
            "message": error["msg"]
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log the error with traceback
    logging.error(
        f"Unhandled error on endpoint {request.url}",
        exc_info=exc
    )
    
    # Handle ValidationError
    if isinstance(exc, ValidationError):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.error,
                "message": exc.message
            }
        )
    
    # Handle other custom errors
    if isinstance(exc, (DatabaseError, NotFoundError, AuthenticationError)):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "Server error",
                "message": exc.detail
            }
        )
    
    # Generic error for unexpected exceptions
    return JSONResponse(
        status_code=500,
        content={
            "error": "Server error",
            "message": "Internal server error"
        }
    )

@app.get("/", response_class=RedirectResponse, status_code=302)
async def root():
    return "/docs"