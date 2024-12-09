from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from app.domain.models.auth.user import User
from app.domain.repositories.auth.user_repo import UserRepository
from app.infrastructure.database.models.auth import UserModel
from app.domain.models.auth.user_role import UserRole
from sqlalchemy import asc
from app.core.exceptions import DatabaseError
import logging

logger = logging.getLogger(__name__)

class PostgresUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, email: str, full_name: str, hashed_password: str, role: UserRole = UserRole.USER) -> User:
        db_user = UserModel(
            email=email,
            full_name=full_name,
            hashed_password=hashed_password,
            role=role
        )
        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)

        return User(
            id=db_user.id,
            email=db_user.email,
            full_name=db_user.full_name,
            hashed_password=db_user.hashed_password,
            role=db_user.role,
            created_at=db_user.created_at
        )

    async def get_by_email(self, email: str) -> Optional[User]:
        query = select(UserModel).where(UserModel.email == email)
        result = await self.session.execute(query)
        db_user = result.scalar_one_or_none()
        
        if db_user:
            return User(
                id=db_user.id,
                email=db_user.email,
                full_name=db_user.full_name,
                hashed_password=db_user.hashed_password,
                role=db_user.role,
                created_at=db_user.created_at
            )
        return None

    async def get_by_id(self, user_id: int) -> Optional[User]:
        query = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(query)
        db_user = result.scalar_one_or_none()
        
        if db_user:
            return User(
                id=db_user.id,
                email=db_user.email,
                full_name=db_user.full_name,
                hashed_password=db_user.hashed_password,
                role=db_user.role,
                created_at=db_user.created_at
            )
        return None

    async def update_refresh_token(self, user_id: int, refresh_token: str | None) -> None:
        query = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(query)
        db_user = result.scalar_one_or_none()
        
        if db_user:
            db_user.refresh_token = refresh_token
            await self.session.commit()

    async def get_all(self) -> List[User]:
        try:
            query = select(UserModel).order_by(asc(UserModel.id))
            result = await self.session.execute(query)
            db_users = result.scalars().all()
            
            return [
                User(
                    id=user.id,
                    email=user.email,
                    full_name=user.full_name,
                    hashed_password=user.hashed_password,
                    role=user.role,
                    created_at=user.created_at
                )
                for user in db_users
            ]
        except Exception as e:
            logger.error(f"Error getting all users: {str(e)}")
            raise DatabaseError(f"Failed to get users: {str(e)}")