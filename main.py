import logging
import sys
from typing import List

# Configure logging at the top
logging.getLogger().handlers = []
logging.basicConfig(level=logging.WARNING)  # Set global level to WARNING

# Configure our app logger
app_logger = logging.getLogger("app")
app_logger.setLevel(logging.INFO)
app_logger.propagate = False

# Create handler with simple format
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(
    logging.Formatter(
        '%(asctime)s - %(message)s',
        datefmt='%H:%M:%S'
    )
)
app_logger.handlers = [handler]

# Now import everything else
from fastapi import FastAPI, Request, status
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.cors import CORSMiddleware
from app.api.routes import (
    store_brands,
    store_locations,
    auth,
    users,
    categories,
    products,
    product_entries,
    health
)
from app.core.exceptions import DatabaseError, NotFoundError, ValidationError, AuthenticationError
from app.infrastructure.logging.logger import get_logger
from app.services.cache_service import init_cache
from app.core.container import Container

logger = get_logger(__name__)

# Add after imports, before FastAPI initialization
ALLOWED_ORIGINS: List[str] = [
    "http://localhost:3000",
    "https://cijene-me-admin.vercel.app",
    "https://cijene-me-admin-*.vercel.app"
]

app = FastAPI(
    title="Cijene.me API",
    description="""
    API for tracking and comparing product prices across different stores in Montenegro.
    
    ## Authentication
    To use protected endpoints:
    1. Use /auth/login to get access token
    2. Click 'Authorize' button and enter token as: Bearer <your_token>
    
    ## Features
    * User Authentication
    * Store Management
    * Product Price Tracking
    * Price History
    """,
    version="1.0.0",
    contact={
        "name": "Savo Lekovic",
        "url": "https://www.google.com"
    },
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "User authentication and authorization operations"
        },
        {
            "name": "Users",
            "description": "User management operations"
        },
        {
            "name": "Store Brands",
            "description": "Store brand management"
        },
        {
            "name": "Store Locations",
            "description": "Store location management"
        },
        {
            "name": "Categories",
            "description": "Product category management"
        },
        {
            "name": "Products",
            "description": "Product management"
        },
        {
            "name": "Product Entries",
            "description": "Product price entries and history"
        }
    ],
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": True,
    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    try:
        response = await call_next(request)
        app_logger.info(f"{request.method} {request.url.path} - {response.status_code}")
        return response
    except ValidationError as ve:
        # Handle ValidationError specifically
        response = JSONResponse(
            status_code=400,
            content={
                "error": "Validation error",
                "message": str(ve)
            }
        )
        app_logger.info(f"{request.method} {request.url.path} - 400 - {str(ve)}")
        return response
    except Exception as e:
        app_logger.error(f"{request.method} {request.url.path} - {str(e)}")
        raise

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(store_brands.router)
app.include_router(store_locations.router)
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(product_entries.router)
app.include_router(health.router)

# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    
    if any(error["type"] == "missing" for error in errors):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "Validation error",
                "message": "Request body is required"
            }
        )
    
    if any(error["type"] == "value_error.email" for error in errors):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "Validation error",
                "message": "Enter a valid email address."
            }
        )
    
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
    if isinstance(exc, ValidationError):
        return JSONResponse(
            status_code=400,
            content={
                "error": "Validation error",
                "message": str(exc)
            }
        )
    
    if isinstance(exc, (DatabaseError, NotFoundError, AuthenticationError)):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.error if hasattr(exc, 'error') else "Server error",
                "message": exc.detail if hasattr(exc, 'detail') else str(exc)
            }
        )
    
    app_logger.error(f"Unhandled error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Server error",
            "message": "Internal server error"
        }
    )

# Root redirect
@app.get("/", response_class=RedirectResponse, status_code=302, include_in_schema=False)
async def root():
    return "/docs"

# Update the security scheme configuration
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
        
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add security scheme
    openapi_schema["components"] = {
        "securitySchemes": {
            "Bearer": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            }
        },
        "schemas": {
            "UserLogin": {
                "title": "UserLogin",
                "type": "object",
                "properties": {
                    "email": {"type": "string", "format": "email"},
                    "password": {"type": "string"}
                },
                "required": ["email", "password"]
            },
            "UserCreate": {
                "title": "UserCreate",
                "type": "object",
                "properties": {
                    "email": {"type": "string", "format": "email"},
                    "full_name": {"type": "string"},
                    "password": {"type": "string"}
                },
                "required": ["email", "full_name", "password"]
            }
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.middleware("http")
async def handle_500_errors(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Internal Server Error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": "An unexpected error occurred"
            }
        )

@app.on_event("startup")
async def startup():
    await init_cache()

# Create container
container = Container()

# Wire container
container.wire(
    modules=[
        "app.api.routes.products",
        "app.api.routes.users",
        "app.api.routes.categories",
        "app.api.routes.product_entries",
        "app.api.routes.store_brands",
        "app.api.routes.store_locations"
    ]
)

# Add container to app
app.container = container