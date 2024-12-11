import logging
import sys

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
from fastapi.middleware.cors import CORSMiddleware
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

logger = get_logger(__name__)

app = FastAPI(
    title="Cijene.me API",
    description="""
    API for tracking and comparing product prices across different stores in Montenegro.
    
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
    ]
)

origins = [
    "http://localhost:3000",
    "localhost:3000",
    "https://cijene-me-admin.vercel.app",
    "http://cijene-me-admin.vercel.app",
    "https://cijene-me-api.onrender.com",
    "http://cijene-me-api.onrender.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
    allow_origin_regex=None
)

# Add CORS headers middleware
@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = request.headers.get("Origin", "*")
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

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