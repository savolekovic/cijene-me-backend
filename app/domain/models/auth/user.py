from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from .user_role import UserRole
from app.infrastructure.database.database import get_current_time

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
    created_at: datetime = Field(default_factory=get_current_time)
