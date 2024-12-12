from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.api.responses.auth import UserResponse
from app.domain.models.auth import User, UserRole
from app.infrastructure.repositories.auth.postgres_user_repository import PostgresUserRepository
from app.api.dependencies.auth import get_current_user, get_current_admin
from app.api.dependencies.services import get_user_repository
from app.core.exceptions import DatabaseError, NotFoundError
from app.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/me", 
    response_model=UserResponse,
    summary="Get current user",
    description="Get details of currently authenticated user.",
    responses={
        401: {"description": "Unauthorized",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Authorization error",
                        "message": "Cannot assign ADMIN role to other users"
                    }
                }
            }},
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Authorization error",
                        "message": "Cannot assign ADMIN role to other users"
                    }
                }
            }
        },
    },
     openapi_extra={
        "responses": {
            "422": None
        }
    }
)
async def read_users_me(
    current_user: User = Depends(get_current_user)
):
    logger.info(f"Fetching current user info for user_id: {current_user.id}")
    return current_user

@router.get("/", 
    response_model=List[UserResponse],
    summary="Get all non-admin users",
    description="Get list of all non-admin users. Requires admin privileges.",
    responses={
        401: {"description": "Unauthorized",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Authorization error",
                        "message": "Unauthorized to get all users"
                    }
                }
            }},
        403: {"description": "Forbidden",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Authorization error",
                        "message": "Not enough privileges to get all users"
                    }
                }
            }
        }
    },
     openapi_extra={
        "responses": {
            "422": None
        }
    }
)
async def get_all_users(
    current_user: User = Depends(get_current_admin),
    user_repo: PostgresUserRepository = Depends(get_user_repository)
):
    try:
        logger.info("Admin requesting all non-admin users list")
        users = await user_repo.get_all_users()
        logger.info(f"Retrieved {len(users)} non-admin users")
        return users
    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
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
            "description": "Forbidden",
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
            "description": "Not found",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Not found",
                        "message": "User with id {id} not found"
                    }
                }
            }
        }
    },
     openapi_extra={
        "responses": {
            "422": None
        }
    }

)
async def update_user_role(
    user_id: int,
    role: UserRole,
    current_user: User = Depends(get_current_admin),
    user_repo: PostgresUserRepository = Depends(get_user_repository)
):
    logger.info(f"Updating role for user_id {user_id} to {role}")
    if role == UserRole.ADMIN and current_user.id != user_id:
        logger.warning(f"Attempt to assign ADMIN role to user_id {user_id} denied")
        raise HTTPException(
            status_code=403,
            detail="Cannot assign ADMIN role to other users"
        )
    
    updated_user = await user_repo.update_role(user_id, role)
    logger.info(f"Successfully updated role for user_id {user_id}")
    return updated_user 

@router.delete("/delete/{user_id}", 
    summary="Delete user",
    description="""Delete a user account. Only admins are authorized to delete any user.""",
    responses={
        200: {
            "description": "User deleted successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "User deleted successfully"
                    }
                }
            }
        },
        401: {"description": "Unauthorized",
              "content": {
                "application/json": {
                    "example": {
                        "error": "Authorization error",
                        "message": "Unauthorized to delete user"
                    }
                }
            }},
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Authorization error",
                        "message": "Cannot delete admin users"
                    }
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Not found",
                        "message": "User not found"
                    }
                }
            }
        }
    },
     openapi_extra={
        "responses": {
            "422": None
        }
    }
)
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    user_repo: PostgresUserRepository = Depends(get_user_repository)
):
    try:
        # Check if user exists
        user_to_delete = await user_repo.get_by_id(user_id)
        if not user_to_delete:
            raise NotFoundError("User", user_id)

        # Authorization checks
        if user_to_delete.role == UserRole.ADMIN:
            logger.warning(f"Attempt to delete admin user {user_id} denied")
            raise HTTPException(
                status_code=403,
                detail="Cannot delete admin users"
            )

        # Perform deletion
        success = await user_repo.delete(user_id)
        if not success:
            raise DatabaseError("Failed to delete user")

        logger.info(f"User {user_id} deleted successfully")
        return {"message": "User deleted successfully"}

    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {str(e)}")
        raise