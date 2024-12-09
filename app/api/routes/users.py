from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.domain.models.auth import User, UserRole
from app.infrastructure.database.database import get_db
from app.infrastructure.repositories.auth.postgres_user_repository import PostgresUserRepository
from app.api.dependencies.auth import get_current_user, get_current_admin
from app.domain.models.responses.auth_responses import UserResponse

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/me", 
    response_model=UserResponse,
    responses={
        200: {
            "description": "Current user information",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "email": "user@example.com",
                        "full_name": "John Doe",
                        "role": "user",
                        "created_at": "2024-01-08T12:00:00"
                    }
                }
            }
        },
        401: {
            "description": "Not authenticated",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Authentication error",
                        "message": "Not authenticated"
                    }
                }
            }
        }
    },
    openapi_extra={
        "security": [{"Bearer": []}]
    }
)
async def read_users_me(
    current_user: User = Depends(get_current_user)
):
    return current_user

@router.get("/", 
    response_model=List[UserResponse],
    responses={
        200: {
            "description": "List of all users",
            "content": {
                "application/json": {
                    "example": [{
                        "id": 1,
                        "email": "user@example.com",
                        "full_name": "John Doe",
                        "role": "user",
                        "created_at": "2024-01-08T12:00:00"
                    }]
                }
            }
        },
        401: {
            "description": "Not authenticated",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Authentication error",
                        "message": "Not authenticated"
                    }
                }
            }
        },
        403: {
            "description": "Not enough privileges",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Authorization error",
                        "message": "Admin privileges required"
                    }
                }
            }
        }
    },
    openapi_extra={
        "security": [{"Bearer": []}]
    }
)
async def get_all_users(
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    repository = PostgresUserRepository(db)
    return await repository.get_all()

@router.put("/{user_id}/role", 
    response_model=UserResponse,
    responses={
        200: {
            "description": "User role updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "email": "user@example.com",
                        "full_name": "John Doe",
                        "role": "mediator",
                        "created_at": "2024-01-08T12:00:00"
                    }
                }
            }
        },
        401: {
            "description": "Not authenticated",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Authentication error",
                        "message": "Not authenticated"
                    }
                }
            }
        },
        403: {
            "description": "Not enough privileges",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Authorization error",
                        "message": "Admin privileges required"
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
                        "message": "User with id 1 not found"
                    }
                }
            }
        }
    },
    openapi_extra={
        "security": [{"Bearer": []}]
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