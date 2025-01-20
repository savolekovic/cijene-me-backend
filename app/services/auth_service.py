from datetime import datetime, timedelta
from typing import Optional, Tuple
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.domain.models.auth import User, TokenPayload, UserRole
from app.domain.repositories.auth.user_repo import UserRepository
from app.infrastructure.database.database import get_current_time
from app.infrastructure.logging.logger import get_logger
from app.core.exceptions import AuthenticationError
from app.core.config import settings
from dotenv import load_dotenv
import re
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException


load_dotenv()
logger = get_logger(__name__)

# Use settings from config.py
SECRET_KEY = settings.JWT_SECRET_KEY
REFRESH_SECRET_KEY = settings.JWT_REFRESH_SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def validate_password(self, password: str) -> bool:
        """
        Password must be at least 8 characters long and contain:
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one number
        - At least one special character
        """
        if len(password) < 8:
            return False
        if not re.search(r"[A-Z]", password):
            return False
        if not re.search(r"[a-z]", password):
            return False
        if not re.search(r"\d", password):
            return False
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False
        return True

    def get_password_hash(self, password: str) -> str:
        if not self.validate_password(password):
            raise ValueError(
                "Password must be at least 8 characters long and contain uppercase, "
                "lowercase, number and special characters"
            )
        return pwd_context.hash(password)

    async def authenticate_user(self, email: str, password: str, db: AsyncSession) -> Optional[User]:
        try:
            user = await self.user_repo.get_by_email(email, db)
            if not user:
                return None
            if not self.verify_password(password, user.hashed_password):
                return None
            return user
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            raise

    def create_access_token(self, user_id: int, role: UserRole) -> str:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        expire = datetime.utcnow() + expires_delta
        to_encode = {
            "sub": str(user_id),
            "exp": int(expire.timestamp()),
            "token_type": "access",
            "role": role.value
        }
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    def create_refresh_token(self, user_id: int) -> str:
        expires_delta = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        expire = get_current_time() + expires_delta
        to_encode = {
            "sub": str(user_id),
            "exp": expire,
            "token_type": "refresh"
        }
        return jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)

    async def get_current_user(self, token: str, db: AsyncSession) -> Optional[User]:
        try:
            # Decode JWT token
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            token_data = TokenPayload(**payload)
            
            # Check if token is expired
            if datetime.fromtimestamp(token_data.exp) < datetime.now():
                logger.warning("Token has expired")
                raise HTTPException(
                    status_code=401,
                    detail="Token has expired"
                )
            
            # Get user from database
            user = await self.user_repo.get_by_id(int(token_data.sub), db)
            if not user:
                logger.warning(f"No user found for sub: {token_data.sub}")
                raise HTTPException(
                    status_code=401,
                    detail="User not found"
                )
            
            return user
        except JWTError as e:
            logger.error(f"JWT validation error: {str(e)}")
            raise HTTPException(
                status_code=401,
                detail=f"Invalid token format: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected auth error: {str(e)}")
            raise HTTPException(
                status_code=401,
                detail="Authentication failed"
            )

    async def verify_refresh_token(self, refresh_token: str) -> Optional[int]:
        try:
            payload = jwt.decode(refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
            token_data = TokenPayload(**payload)
            if token_data.token_type != "refresh":
                return None
            return int(token_data.sub)
        except JWTError:
            return None

    def is_token_expired(self, token: str) -> bool:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            exp = datetime.fromtimestamp(payload["exp"])
            return get_current_time() > exp
        except JWTError:
            return True

    async def get_admin_user(self, token: str, db: AsyncSession) -> Optional[User]:
        user = await self.get_current_user(token, db)
        if user and user.role == UserRole.ADMIN:
            return user
        return None

    async def refresh_tokens(self, refresh_token: str, db: AsyncSession) -> Optional[Tuple[str, str]]:
        try:
            user_id = await self.verify_refresh_token(refresh_token)
            if not user_id:
                logger.warning("Invalid refresh token")
                return None
            
            user = await self.user_repo.get_by_id(user_id, db)
            if not user:
                logger.warning(f"User not found for refresh token: {user_id}")
                return None

            new_access_token = self.create_access_token(user.id, user.role)
            new_refresh_token = self.create_refresh_token(user.id)
            
            await self.user_repo.update_refresh_token(user.id, new_refresh_token, db)
            logger.info(f"Tokens refreshed for user: {user_id}")
            
            return new_access_token, new_refresh_token
        except Exception as e:
            logger.error(f"Error refreshing tokens: {str(e)}")
            raise

    async def register_user(self, email: str, password: str, full_name: str, db: AsyncSession) -> User:
        try:
            logger.info(f"Attempting to register new user: {email}")
            # Check if user already exists
            existing_user = await self.user_repo.get_by_email(email, db)
            if existing_user:
                logger.warning(f"User already exists: {email}")
                raise AuthenticationError("User with this email already exists")

            hashed_password = self.get_password_hash(password)
            user = await self.user_repo.create(
                email=email,
                hashed_password=hashed_password,
                full_name=full_name,
                db=db
            )
            logger.info(f"Successfully registered user: {email}")
            return user
        except Exception as e:
            logger.error(f"Error registering user: {str(e)}")
            raise

    async def logout_user(self, user_id: int, db: AsyncSession) -> bool:
        try:
            logger.info(f"Logging out user: {user_id}")
            await self.user_repo.update_refresh_token(user_id, None, db)
            logger.info(f"Successfully logged out user: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error logging out user: {str(e)}")
            raise