import logging
import sys

# Configure root logger to be silent
logging.getLogger().handlers = []
logging.basicConfig(level=logging.CRITICAL)

# Configure our app logger
app_logger = logging.getLogger("app")
app_logger.setLevel(logging.INFO)
app_logger.propagate = False

# Create custom handler
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(
    logging.Formatter(
        '%(asctime)s - %(message)s',
        datefmt='%H:%M:%S'
    )
)

# Set handler
app_logger.handlers = [handler]

# Now import everything else
from fastapi import FastAPI, Request, status
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.exceptions import RequestValidationError
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
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    responses={},
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "Endpoints for user authentication and authorization"
        },
        {
            "name": "Users",
            "description": "Endpoints for user management and profile operations"
        }
    ]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://cijene.me"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Content-Type", 
        "Authorization", 
        "Accept",
        "Origin",
        "X-Requested-With"
    ],
    expose_headers=["*"],
    max_age=600
)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    try:
        response = await call_next(request)
        app_logger.info(f"{request.method} {request.url.path} - {response.status_code}")
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
            status_code=exc.status_code,
            content={
                "error": exc.error,
                "message": exc.message
            }
        )
    
    if isinstance(exc, (DatabaseError, NotFoundError, AuthenticationError)):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "Server error",
                "message": exc.detail
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