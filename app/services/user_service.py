from app.domain.repositories.auth.user_repo import UserRepository
from app.services.cache_service import CacheManager
from app.domain.models.auth import User, UserRole
from app.infrastructure.logging.logger import get_logger
from app.core.exceptions import NotFoundError
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.responses.auth import PaginatedUserResponse

logger = get_logger(__name__)

class UserService:
    def __init__(self, user_repo: UserRepository, cache_manager: CacheManager):
        self.user_repo = user_repo
        self.cache_manager = cache_manager

    async def get_all_users(self, db: AsyncSession, page: int = 1, per_page: int = 10, search: str = None, order_by: str = "full_name", order_direction: str = "asc") -> PaginatedUserResponse:
        try:
            logger.info(f"Fetching users with pagination (page={page}, per_page={per_page}) and search='{search}', order_by={order_by}, order_direction={order_direction}")
            return await self.user_repo.get_all_users(
                db=db,
                page=page,
                per_page=per_page,
                search=search,
                order_by=order_by,
                order_direction=order_direction
            )
        except Exception as e:
            logger.error(f"Error fetching users: {str(e)}")
            raise

    async def get_user(self, user_id: int, db: AsyncSession) -> User:
        try:
            logger.info(f"Fetching user with id: {user_id}")
            user = await self.user_repo.get_by_id(user_id, db)
            if not user:
                logger.warning(f"User not found: {user_id}")
                raise NotFoundError("User", user_id)
            return user
        except Exception as e:
            logger.error(f"Error fetching user {user_id}: {str(e)}")
            raise

    async def update_user_role(self, user_id: int, role: UserRole, db: AsyncSession) -> User:
        try:
            logger.info(f"Updating role for user {user_id} to {role}")
            updated_user = await self.user_repo.update_role(user_id, role, db)
            if not updated_user:
                raise NotFoundError("User", user_id)
            return updated_user
        except Exception as e:
            logger.error(f"Error updating user role: {str(e)}")
            raise

    async def delete_user(self, user_id: int, db: AsyncSession) -> bool:
        try:
            logger.info(f"Attempting to delete user {user_id}")
            success = await self.user_repo.delete(user_id, db)
            if not success:
                logger.warning(f"User not found: {user_id}")
                raise NotFoundError("User", user_id)
            await self.cache_manager.clear_user_related_caches()
            return True
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            raise 