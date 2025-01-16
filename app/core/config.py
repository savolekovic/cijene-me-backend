from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Environment
    ENV: str = os.getenv("ENV", "development")
    
    # Database settings
    DB_USER: str = "postgres"
    DB_PASSWORD: Optional[str] = None
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_NAME: str = "cijene_me_db"
    DATABASE_URL: Optional[str] = None

    # JWT Settings - make them Optional with None default
    JWT_SECRET_KEY: Optional[str] = None
    JWT_REFRESH_SECRET_KEY: Optional[str] = None
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Cache settings
    REDIS_URL: Optional[str] = None
    USE_CACHE: bool = True
    CACHE_PREFIX: str = "cijene-me:"
    CACHE_TIME_SHORT: int = 300    # 5 minutes
    CACHE_TIME_MEDIUM: int = 1800  # 30 minutes
    CACHE_TIME_LONG: int = 3600    # 1 hour

    class Config:
        env_file = ".env"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Set development defaults if not in production
        if self.ENV != "production":
            if not self.JWT_SECRET_KEY:
                self.JWT_SECRET_KEY = "dev-secret-key-not-secure"
            if not self.JWT_REFRESH_SECRET_KEY:
                self.JWT_REFRESH_SECRET_KEY = "dev-refresh-key-not-secure"
            if not self.DATABASE_URL:
                self.DATABASE_URL = f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        else:
            # In production, ensure required values are set
            if not self.JWT_SECRET_KEY or not self.JWT_REFRESH_SECRET_KEY:
                # Use environment variables directly as fallback
                self.JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
                self.JWT_REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY")
                
                if not self.JWT_SECRET_KEY or not self.JWT_REFRESH_SECRET_KEY:
                    raise ValueError(
                        "JWT_SECRET_KEY and JWT_REFRESH_SECRET_KEY must be set in production"
                    )

    @property
    def get_database_url(self) -> str:
        """Get database URL, prioritizing DATABASE_URL if set"""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

settings = Settings() 