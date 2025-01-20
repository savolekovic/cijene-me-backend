from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.models.auth import User, UserRole
from app.infrastructure.database.database import get_db
from app.infrastructure.repositories.auth.postgres_user_repository import PostgresUserRepository
from app.services.auth_service import AuthService
import logging

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
logger = logging.getLogger(__name__)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    logger.info(f"Attempting to validate token: {token[:20]}...")  # Log first 20 chars for security
    try:
        repository = PostgresUserRepository(db)
        auth_service = AuthService(repository)
        user = await auth_service.get_current_user(token, db)
        if not user:
            logger.warning("No user found for token")
            raise HTTPException(
                status_code=401,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        logger.info(f"Successfully authenticated user {user.id} with role {user.role}")
        return user
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

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
    logger.info(f"Checking privileges for user: {current_user.id} with role: {current_user.role}")
    if current_user.role not in [UserRole.ADMIN, UserRole.MODERATOR]:
        logger.warning(f"User {current_user.id} attempted privileged action with role: {current_user.role}")
        raise HTTPException(
            status_code=403,
            detail="Admin or moderator privileges required",
        )
    return current_user 