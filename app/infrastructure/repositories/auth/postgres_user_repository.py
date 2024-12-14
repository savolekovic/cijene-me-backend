from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
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
    def __init__(self, session: AsyncSession = None):
        pass

    async def create(self, email: str, full_name: str, hashed_password: str, role: UserRole = UserRole.USER, db: AsyncSession = None) -> User:
        db_user = UserModel(
            email=email,
            full_name=full_name,
            hashed_password=hashed_password,
            role=role
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)

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

    async def get_by_email(self, email: str, db: AsyncSession) -> Optional[User]:
        query = select(UserModel).where(UserModel.email == email)
        result = await db.execute(query)
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

    async def get_by_id(self, user_id: int, db: AsyncSession) -> Optional[User]:
        query = select(UserModel).where(UserModel.id == user_id)
        result = await db.execute(query)
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

    async def update_refresh_token(self, user_id: int, refresh_token: str | None, db: AsyncSession) -> None:
        query = select(UserModel).where(UserModel.id == user_id)
        result = await db.execute(query)
        db_user = result.scalar_one_or_none()
        
        if db_user:
            db_user.refresh_token = refresh_token
            await db.commit()

    async def get_all_users(self, db: AsyncSession) -> List[User]:
        try:
            query = select(UserModel)\
                .where(UserModel.role != UserRole.ADMIN)\
                .order_by(asc(UserModel.id))
            result = await db.execute(query)
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
            logger.error(f"Error getting non-admin users: {str(e)}")
            raise DatabaseError(f"Failed to get users: {str(e)}")

    async def delete(self, user_id: int, db: AsyncSession) -> bool:
        try:
            query = select(UserModel).where(UserModel.id == user_id)
            result = await db.execute(query)
            user = result.scalar_one_or_none()
            
            if user:
                await db.delete(user)
                await db.commit()
                logger.info(f"Successfully deleted user with id {user_id}")
                return True
                
            logger.warning(f"No user found with id {user_id} for deletion")
            return False
            
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {str(e)}")
            raise DatabaseError(f"Failed to delete user: {str(e)}")

    async def update_role(self, user_id: int, role: UserRole, db: AsyncSession) -> Optional[User]:
        try:
            result = await db.execute(
                select(UserModel).where(UserModel.id == user_id)
            )
            user_db = result.scalar_one_or_none()
            if user_db:
                user_db.role = role.value
                await db.flush()
                await db.commit()
                return User(
                    id=user_db.id,
                    email=user_db.email,
                    full_name=user_db.full_name,
                    hashed_password=user_db.hashed_password,
                    role=user_db.role,
                    created_at=user_db.created_at
                )
            return None
        except Exception as e:
            logger.error(f"Error updating user role: {str(e)}")
            await db.rollback()
            raise