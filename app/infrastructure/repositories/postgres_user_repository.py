from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.domain.models.user import User
from app.domain.repositories.user_repo import UserRepository
from app.infrastructure.database.models.user import UserModel

class PostgresUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, email: str, username: str, hashed_password: str) -> User:
        db_user = UserModel(
            email=email,
            username=username,
            hashed_password=hashed_password
        )
        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)

        return User(
            id=db_user.id,
            email=db_user.email,
            username=db_user.username,
            hashed_password=db_user.hashed_password,
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
                username=db_user.username,
                hashed_password=db_user.hashed_password,
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
                username=db_user.username,
                hashed_password=db_user.hashed_password,
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