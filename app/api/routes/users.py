from fastapi import APIRouter, HTTPException, Depends, Query
from app.api.responses.auth import UserResponse, PaginatedUserResponse
from app.domain.models.auth import User, UserRole
from app.api.dependencies.auth import get_current_user, get_current_admin
from app.infrastructure.database.database import get_db
from app.infrastructure.logging.logger import get_logger
from fastapi_cache.decorator import cache
from app.core.config import settings
from app.core.container import Container
from app.services.user_service import UserService
from dependency_injector.wiring import Provide, inject
from app.api.models.user import UpdateUserRoleRequest
from sqlalchemy.ext.asyncio import AsyncSession

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
@inject
async def read_users_me(
    current_user: User = Depends(get_current_user)
):
    logger.info(f"Fetching current user info for user_id: {current_user.id}")
    return current_user

@router.get("/", 
    response_model=PaginatedUserResponse,
    summary="Get all non-admin users",
    description="Get list of all non-admin users with pagination and search. Requires admin privileges.",
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
@cache(expire=settings.CACHE_TIME_MEDIUM, namespace="users")
@inject
async def get_all_users(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    search: str = Query(None, description="Search query for filtering users by username or email"),
    order_by: str = Query("full_name", description="Field to order by (full_name, email, created_at)"),
    order_direction: str = Query("asc", description="Order direction (asc or desc)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
    user_service: UserService = Depends(Provide[Container.user_service])
) -> PaginatedUserResponse:
    """
    Get all non-admin users with pagination and optional search.
    
    Args:
        page: Page number (default: 1)
        per_page: Number of items per page (default: 10, max: 100)
        search: Optional search query to filter users by username or email
        order_by: Field to order by (default: full_name)
        order_direction: Order direction (asc or desc) (default: asc)
        db: Database session
        current_user: Current admin user
        user_service: User service instance
        
    Returns:
        PaginatedUserResponse containing the paginated list of non-admin users
    """
    try:
        logger.info(f"Getting users - page: {page}, per_page: {per_page}, search: {search}, order_by: {order_by}, order_direction: {order_direction}")
        return await user_service.get_all_users(
            db=db,
            page=page,
            per_page=per_page,
            search=search,
            order_by=order_by,
            order_direction=order_direction
        )
    except Exception as e:
        logger.error(f"Error getting users: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{user_id}/role", 
    response_model=UserResponse,
    summary="Update user role",
    description="""
    Update role of a specific user. Requires admin privileges.
    Note: Admin cannot assign ADMIN role to other users.
    Available roles: USER, MODERATOR, ADMIN
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
@inject
async def update_user_role(
    user_id: int,
    role_update: UpdateUserRoleRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
    user_service: UserService = Depends(Provide[Container.user_service])
):
    if role_update.role == UserRole.ADMIN and current_user.id != user_id:
        logger.warning(f"Attempt to assign ADMIN role to user_id {user_id} denied")
        raise HTTPException(
            status_code=403,
            detail="Cannot assign ADMIN role to other users"
        )
    return await user_service.update_user_role(user_id, role_update.role, db)
    
    

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
@inject
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
    user_service: UserService = Depends(Provide[Container.user_service])
):
    # Check if user exists and is not admin
    user_to_delete = await user_service.get_user(user_id, db)
    if user_to_delete.role == UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Cannot delete admin users"
        )
    
    await user_service.delete_user(user_id, db)
    return {"message": "User deleted successfully"}