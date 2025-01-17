from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.models.auth import User, UserRole
from app.infrastructure.database.database import get_db
from app.infrastructure.repositories.auth.postgres_user_repository import PostgresUserRepository
from app.services.auth_service import AuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    repository = PostgresUserRepository(db)
    auth_service = AuthService(repository)
    user = await auth_service.get_current_user(token, db)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Admin privileges required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user

async def get_current_privileged_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Check if user is either ADMIN or MODERATOR"""
    if current_user.role == UserRole.USER:
        raise HTTPException(
            status_code=403,
            detail="Insufficient privileges",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user 