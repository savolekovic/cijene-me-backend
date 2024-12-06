from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from .user_role import UserRole

class User(BaseModel):
    id: int | None = None
    email: EmailStr
    username: str
    hashed_password: str
    role: UserRole = Field(default=UserRole.USER)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    role: UserRole = UserRole.USER

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: int
    exp: datetime
    token_type: str 