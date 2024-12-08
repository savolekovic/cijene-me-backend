from abc import ABC, abstractmethod
from typing import Optional
from app.domain.models.auth.user import User

class UserRepository(ABC):
    @abstractmethod
    async def create(self, email: str, username: str, hashed_password: str) -> User:
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    async def update_refresh_token(self, user_id: int, refresh_token: str | None) -> None:
        pass