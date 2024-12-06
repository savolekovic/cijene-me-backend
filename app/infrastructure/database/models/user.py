from sqlalchemy import Column, String, DateTime, Integer, Enum
from datetime import datetime
from app.infrastructure.database.database import Base
from app.domain.models.user_role import UserRole

class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.USER)
    refresh_token = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow) 