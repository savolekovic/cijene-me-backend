from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, constr
from typing import Annotated
from .user_role import UserRole

class User(BaseModel):
    id: int | None = None
    email: EmailStr
    full_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        pattern=r'^[a-zA-ZÀ-ÿ\s\'-]+$',  # Letters, spaces, apostrophes, hyphens
        description="Full name (2-100 characters, letters, spaces, and - ' characters allowed)"
    )
    hashed_password: str
    role: UserRole = Field(default=UserRole.USER)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        pattern=r'^[a-zA-ZÀ-ÿ\s\'-]+$',
        description="Full name (2-100 characters, letters, spaces, and - ' characters allowed)"
    )
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "full_name": "John Doe",
                "password": "StrongP@ss123"
            }
        }

class UserLogin(BaseModel):
    email: EmailStr
    password: str
