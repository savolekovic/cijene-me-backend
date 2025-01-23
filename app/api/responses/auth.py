from datetime import datetime
from pydantic import BaseModel, EmailStr
from app.domain.models.auth.user_role import UserRole
from app.api.responses.common import PaginatedResponse

class UserResponse(BaseModel):
    id: int | None = None
    email: EmailStr
    full_name: str
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True

# Use the generic PaginatedResponse with UserResponse
PaginatedUserResponse = PaginatedResponse[UserResponse] 