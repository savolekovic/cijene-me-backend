from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.domain.models.auth import User, UserRole
from app.infrastructure.database.database import get_db
from app.infrastructure.repositories.auth.postgres_user_repository import PostgresUserRepository
from app.api.dependencies.auth import get_current_user, get_current_admin
from app.domain.models.responses.auth_responses import UserResponse
from app.core.exceptions import DatabaseError
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/me", 
    response_model=UserResponse,
    summary="Get current user",
    description="Get details of currently authenticated user. Requires authentication.",
)
async def read_users_me(
    current_user: User = Depends(get_current_user)
):
    return current_user

@router.get("/", 
    response_model=List[UserResponse],
    summary="Get all users",
    description="Get list of all users. Requires admin privileges.",
)
async def get_all_users(
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        repository = PostgresUserRepository(db)
        return await repository.get_all()
    except Exception as e:
        logger.error(f"Error in get_all_users: {str(e)}")
        raise DatabaseError(str(e))

@router.put("/{user_id}/role", 
    response_model=UserResponse,
    summary="Update user role",
    description="""
    Update role of a specific user. Requires admin privileges.
    Note: Admin cannot assign ADMIN role to other users.
    Available roles: USER, MEDIATOR, ADMIN
    """,
    responses={
        200: {"description": "Role updated successfully"},
        403: {
            "description": "Permission denied",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Authorization error",
                        "message": "Cannot assign ADMIN role to other users"
                    }
                }
            }
        },
        404: {
            "description": "User not found",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Not found",
                        "message": "User with id {id} not found"
                    }
                }
            }
        }
    }
)
async def update_user_role(
    user_id: int,
    role: UserRole,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    if role == UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot assign ADMIN role to other users"
        )
    
    repository = PostgresUserRepository(db)
    return await repository.update_role(user_id, role) 