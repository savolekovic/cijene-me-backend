from pydantic import BaseModel
from app.domain.models.auth.user_role import UserRole

class UpdateUserRoleRequest(BaseModel):
    role: UserRole 