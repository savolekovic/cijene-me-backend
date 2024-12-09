from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse, RedirectResponse
import logging
from app.api.routes import (
    store_brands,
    store_locations,
    auth,
    categories,
    products,
    product_entries
)
from app.core.exceptions import DatabaseError, NotFoundError, ValidationError, AuthenticationError

app = FastAPI()

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

# Store management routes
app.include_router(store_brands.router)
app.include_router(store_locations.router)

# Product management routes
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(product_entries.router)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log the error with traceback
    logging.error(
        f"Unhandled error on endpoint {request.url}",
        exc_info=exc
    )
    
    # Return appropriate response based on exception type
    if isinstance(exc, (DatabaseError, NotFoundError, ValidationError, AuthenticationError)):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )
    
    # Generic error for unexpected exceptions
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.get("/", response_class=RedirectResponse, status_code=302)
async def root():
    return "/docs"