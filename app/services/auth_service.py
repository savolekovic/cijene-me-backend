from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.domain.models.auth import User, Token, TokenPayload, UserRole
from app.domain.repositories.auth.user_repo import UserRepository
import os
from dotenv import load_dotenv
import re

load_dotenv()

# Configuration from environment variables with defaults
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")
REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY", "your-refresh-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

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

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = await self.user_repository.get_by_email(email)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

    def create_access_token(self, user_id: int, role: UserRole) -> str:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        expire = datetime.utcnow() + expires_delta
        to_encode = {
            "sub": str(user_id),
            "exp": expire,
            "token_type": "access",
            "role": role.value
        }
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    def create_refresh_token(self, user_id: int) -> str:
        expires_delta = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        expire = datetime.utcnow() + expires_delta
        to_encode = {
            "sub": str(user_id),
            "exp": expire,
            "token_type": "refresh"
        }
        return jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)

    async def get_current_user(self, token: str) -> Optional[User]:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            token_data = TokenPayload(**payload)
            if token_data.token_type != "access":
                return None
        except JWTError:
            return None
        
        user = await self.user_repository.get_by_id(int(token_data.sub))
        return user

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
            return datetime.utcnow() > exp
        except JWTError:
            return True

    async def get_admin_user(self, token: str) -> Optional[User]:
        user = await self.get_current_user(token)
        if not user or user.role != UserRole.ADMIN:
            return None
        return user