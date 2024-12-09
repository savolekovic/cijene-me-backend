from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, constr
from typing import Annotated
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
    username: Annotated[str, constr(min_length=3, max_length=50, strip_whitespace=True)]
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "password": "StrongP@ss123"
            }
        }

class UserLogin(BaseModel):
    email: EmailStr
    password: str
