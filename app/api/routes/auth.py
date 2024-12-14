from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies.auth import get_current_user
from app.api.responses.auth import UserResponse
from app.core.container import Container
from app.core.exceptions import DatabaseError, ValidationError
from app.domain.models.auth import User, Token
from app.api.models.auth import UserCreate, UserLogin
from app.infrastructure.database.database import get_db
from app.infrastructure.repositories.auth.postgres_user_repository import PostgresUserRepository
from app.services.auth_service import AuthService
from app.infrastructure.logging.logger import get_logger
from app.services.cache_service import CacheManager
from dependency_injector.wiring import Provide, inject

logger = get_logger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/register", 
    response_model=UserResponse,
    summary="Register new user",
    description="Create a new user account with email and password. Returns user information without password.",
    responses={
        201: {
            "description": "Created",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "email": "user@example.com",
                        "full_name": "John Doe",
                        "role": "user",
                        "created_at": "2024-01-01T12:00:00.000Z"
                    }
                }
            }
        },
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_email": {
                            "value": {
                                "error": "Validation error", 
                                "message": "Enter a valid email address."
                            }
                        }
                    }
                }
            }
        },
        409: {
            "description": "Conflict",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Conflict error",
                        "message": "Email already registered"
                    }
                }
            }
        }
    },
    openapi_extra={
        "responses": {
            "422": None,
            "200": None
        }
    }
)
async def register(
    user_create: UserCreate,
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(Provide[Container.auth_service])
):
    # Validate email format
    if not user_create.email or "@" not in user_create.email:
        raise ValidationError("Invalid email format")
    
    try:
        # Create user with validated data
        user = await auth_service.register_user(
            email=user_create.email.lower(),
            password=user_create.password,
            full_name=user_create.full_name,
            db=db  # Pass db session
        )
        await CacheManager.clear_user_related_caches()
        return user
    except Exception as e:
        raise DatabaseError(str(e))

@router.post("/login", 
    response_model=Token,
    summary="Login user",
    description="Login with email and password. Returns access and refresh tokens.",
    include_in_schema=True,
    responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGc...",
                        "refresh_token": "eyJhbG..."
                    }
                }
            }
        },
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_credentials": {
                            "value": {
                                "error": "Validation error",
                                "message": "Incorrect email or password"
                            }
                        }
                    }
                }
            }
        }
    },
     openapi_extra={
        "responses": {
            "422": None
        }
    }
)
@inject
async def login(
    user_login: UserLogin,
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(Provide[Container.auth_service])
):
    try:
        user = await auth_service.authenticate_user(user_login.email, user_login.password, db)
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Incorrect email or password"
            )
        
        access_token = auth_service.create_access_token(user.id, user.role)
        refresh_token = auth_service.create_refresh_token(user.id)
        
        await auth_service.user_repo.update_refresh_token(user.id, refresh_token, db)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise

@router.post("/refresh",
    response_model=Token,
    summary="Refresh access token",
    description="Get new access token using refresh token. Does not require authentication header.",
    responses={
        401: {"description": "Unauthorized"}
    },
    openapi_extra={
        "responses": {
            "422": None
        }
    }
)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(Provide[Container.auth_service])
):
    try:
        tokens = await auth_service.refresh_tokens(refresh_token, db)  # Pass db session
        if not tokens:
            raise HTTPException(
                status_code=401,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token, new_refresh_token = tokens
        return Token(
            access_token=access_token,
            refresh_token=new_refresh_token
        )
    except Exception as e:
        logger.error(f"Error refreshing token: {str(e)}")
        raise

@router.post("/logout",
    summary="Logout user",
    description="Invalidate the current user's refresh token. Requires authentication.",
    responses={
        401: {"description": "Unauthorized"}
    },
    openapi_extra={
        "responses": {
            "422": None
        }
    }
)
async def logout(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(Provide[Container.auth_service])
):
    await auth_service.logout_user(current_user.id, db)  # Pass db session
    return {"message": "Successfully logged out"}
