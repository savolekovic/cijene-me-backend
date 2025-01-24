from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.domain.models.auth.user import User
from app.domain.repositories.auth.user_repo import UserRepository
from app.infrastructure.database.models.auth import UserModel
from app.domain.models.auth.user_role import UserRole
from sqlalchemy import asc, or_, desc
from app.core.exceptions import DatabaseError
import logging
from app.api.responses.auth import UserResponse, PaginatedUserResponse

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
        try:
            # Use the session directly
            result = await db.execute(
                select(UserModel).where(UserModel.email == email)
            )
            user = result.scalar_one_or_none()
            return user if user else None
        except Exception as e:
            logger.error(f"Error getting user by email: {str(e)}")
            raise

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

    async def get_all_users(self, db: AsyncSession, page: int = 1, per_page: int = 10, search: str = None, order_by: str = "full_name", order_direction: str = "asc") -> PaginatedUserResponse:
        try:
            # Base query for data
            query = select(UserModel).where(UserModel.role != UserRole.ADMIN)
            
            # Base query for count
            count_query = select(UserModel).where(UserModel.role != UserRole.ADMIN)
            
            # Add search filter if search query is provided
            if search:
                search_pattern = f"%{search}%"
                search_filter = or_(
                    UserModel.email.ilike(search_pattern),
                    UserModel.full_name.ilike(search_pattern)
                )
                query = query.where(search_filter)
                count_query = count_query.where(search_filter)
            
            # Get total count
            count_result = await db.execute(select(func.count()).select_from(count_query.subquery()))
            total_count = count_result.scalar()
            
            # Add ordering
            order_column = getattr(UserModel, order_by, UserModel.full_name)
            if order_direction.lower() == "desc":
                query = query.order_by(desc(order_column))
            else:
                query = query.order_by(asc(order_column))
            
            # Add pagination
            offset = (page - 1) * per_page
            query = query.offset(offset).limit(per_page)
            
            # Get paginated data
            result = await db.execute(query)
            users = result.scalars().all()
            
            # Convert to response model
            user_list = [
                UserResponse(
                    id=user.id,
                    email=user.email,
                    full_name=user.full_name,
                    role=user.role,
                    created_at=user.created_at
                )
                for user in users
            ]
            
            return PaginatedUserResponse(
                total_count=total_count,
                data=user_list
            )
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