from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies.auth import get_current_user
from app.core.exceptions import DatabaseError, ValidationError
from app.domain.models.auth import User, UserCreate, Token, UserRole, UserLogin
from app.domain.models.responses.auth_responses import UserResponse
from app.infrastructure.database.database import get_db
from app.infrastructure.repositories.auth.postgres_user_repository import PostgresUserRepository
from app.services.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    repository = PostgresUserRepository(db)
    auth_service = AuthService(repository)
    user = await auth_service.get_current_user(token)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

@router.post("/register", 
    response_model=UserResponse,
    summary="Register new user",
    description="Create a new user account with email and password. Returns user information without password.",
    responses={
        201: {"description": "User created successfully"},
        400: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_email": {
                            "value": {"error": "Validation error", "message": "Enter a valid email address."}
                        },
                        "email_exists": {
                            "value": {"error": "Validation error", "message": "Email already registered"}
                        }
                    }
                }
            }
        }
    }
)
async def register(
    user_create: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    repository = PostgresUserRepository(db)
    auth_service = AuthService(repository)
    
    # Validate email format
    if not user_create.email or "@" not in user_create.email:
        raise ValidationError("Invalid email format")
    
    # Check if user exists first
    existing_user = await repository.get_by_email(user_create.email.lower())
    if existing_user:
        raise ValidationError("Email already registered")
    
    # Create user with validated data
    try:
        user = await repository.create(
            email=user_create.email.lower(),
            full_name=user_create.full_name,
            hashed_password=auth_service.get_password_hash(user_create.password),
            role=UserRole.USER
        )
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
            "description": "Successfully logged in",
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
                        },
                        "invalid_email": {
                            "value": {
                                "error": "Validation error",
                                "message": "Enter a valid email address."
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
async def login(
    user_login: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    repository = PostgresUserRepository(db)
    auth_service = AuthService(repository)
    
    user = await auth_service.authenticate_user(
        email=user_login.email,
        password=user_login.password
    )
    if not user:
        raise ValidationError("Incorrect email or password")
    
    access_token = auth_service.create_access_token(user.id, user.role)
    refresh_token = auth_service.create_refresh_token(user.id)
    
    await repository.update_refresh_token(user.id, refresh_token)
    return Token(access_token=access_token, refresh_token=refresh_token)

@router.post("/refresh",
    response_model=Token,
    summary="Refresh access token",
    description="Get new access token using refresh token. Does not require authentication header."
)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
):
    # No auth needed - uses refresh token instead
    repository = PostgresUserRepository(db)
    auth_service = AuthService(repository)
    
    # Verify refresh token
    user_id = await auth_service.verify_refresh_token(refresh_token)
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create new tokens
    new_access_token = auth_service.create_access_token(user_id)
    new_refresh_token = auth_service.create_refresh_token(user_id)
    
    # Update refresh token in database
    await repository.update_refresh_token(user_id, new_refresh_token)
    
    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token
    )

@router.post("/logout",
    summary="Logout user",
    description="Invalidate the current user's refresh token. Requires authentication.",
)
async def logout(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Logout user by invalidating their refresh token
    """
    repository = PostgresUserRepository(db)
    await repository.update_refresh_token(current_user.id, None)
    return {"message": "Successfully logged out"}
