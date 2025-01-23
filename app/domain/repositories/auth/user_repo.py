from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.models.auth import User, UserRole
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.responses.auth import PaginatedUserResponse

class UserRepository(ABC):
    @abstractmethod
    async def create(self, email: str, full_name: str, hashed_password: str, role: UserRole = UserRole.USER, db: AsyncSession = None) -> User:
        pass

    @abstractmethod
    async def get_by_email(self, email: str, db: AsyncSession) -> Optional[User]:
        pass

    @abstractmethod
    async def get_by_id(self, user_id: int, db: AsyncSession) -> Optional[User]:
        pass

    @abstractmethod
    async def update_refresh_token(self, user_id: int, refresh_token: str | None, db: AsyncSession) -> None:
        pass

    @abstractmethod
    async def get_all_users(self, db: AsyncSession, page: int = 1, per_page: int = 10, search: str = None) -> PaginatedUserResponse:
        """Get a paginated list of all non-admin users with optional search."""
        pass

    @abstractmethod
    async def delete(self, user_id: int, db: AsyncSession) -> bool:
        pass

    @abstractmethod
    async def update_role(self, user_id: int, role: UserRole, db: AsyncSession) -> Optional[User]:
        pass