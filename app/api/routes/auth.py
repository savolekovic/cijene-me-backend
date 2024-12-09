from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from app.api.dependencies.auth import get_current_admin
from app.core.exceptions import DatabaseError
from app.domain.models.auth import User, UserCreate, Token, UserRole
from app.infrastructure.database.database import get_db
from app.infrastructure.repositories.auth.postgres_user_repository import PostgresUserRepository
from app.services.auth_service import AuthService, ACCESS_TOKEN_EXPIRE_MINUTES
from typing import List

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

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

@router.post("/register", response_model=User)
async def register(
    user_create: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    repository = PostgresUserRepository(db)
    auth_service = AuthService(repository)
    
    # Validate email format
    if not user_create.email or "@" not in user_create.email:
        raise ValidationError("Invalid email format")
    
    # Validate username
    if not user_create.username:
        raise ValidationError("Username cannot be empty")
    
    # Validate password
    try:
        hashed_password = auth_service.get_password_hash(user_create.password)
    except ValueError as e:
        raise ValidationError(str(e))
    
    # Check if user exists
    existing_user = await repository.get_by_email(user_create.email)
    if existing_user:
        raise ValidationError("Email already registered")
    
    # Create user with validated data
    try:
        user = await repository.create(
            email=user_create.email.lower(),  # Store email in lowercase
            username=user_create.username.strip(),  # Remove whitespace
            hashed_password=hashed_password,
            role=UserRole.USER
        )
        return user
    except Exception as e:
        raise DatabaseError(str(e))

@router.post("/token", response_model=Token, include_in_schema=False)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    # No auth needed - public endpoint for login
    repository = PostgresUserRepository(db)
    auth_service = AuthService(repository)
    
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
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

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repository = PostgresUserRepository(db)
    await repository.update_refresh_token(current_user.id, None)
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=User)
async def read_users_me(
    current_user: User = Depends(get_current_user)  # Already has auth check
):
    return current_user

# Add new endpoint for admin to manage users
@router.get("/users", response_model=List[User])
async def get_all_users(
    current_user: User = Depends(get_current_admin),  # Only admin can list users
    db: AsyncSession = Depends(get_db)
):
    repository = PostgresUserRepository(db)
    return await repository.get_all()

# Add endpoint for admin to change user roles
@router.put("/users/{user_id}/role", response_model=User)
async def update_user_role(
    user_id: int,
    role: UserRole,
    current_user: User = Depends(get_current_admin),  # Only admin can change roles
    db: AsyncSession = Depends(get_db)
):
    if role == UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot assign ADMIN role to other users"
        )
    
    repository = PostgresUserRepository(db)
    return await repository.update_role(user_id, role) 