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

@router.post("/register", response_model=UserResponse)
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

@router.post("/login", response_model=Token)
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

@router.post("/refresh", response_model=Token)
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
    responses={
        200: {
            "description": "Successfully logged out",
            "content": {
                "application/json": {
                    "example": {"message": "Successfully logged out"}
                }
            }
        },
        401: {
            "description": "Not authenticated",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Authentication error",
                        "message": "Not authenticated"
                    }
                }
            }
        }
    },
    openapi_extra={
        "security": [{"Bearer": []}]
    }
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
