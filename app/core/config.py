from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Environment
    ENV: str = "development"
    
    # Database settings
    DB_USER: str = "postgres"
    DB_PASSWORD: str
    DB_HOST: str = "localhost"
    DB_NAME: str = "cijene_me_db"
    DATABASE_URL: str | None = None
    
    # JWT settings
    JWT_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY: str
    
    # Cache settings
    USE_CACHE: bool = True
    REDIS_URL: str = "redis://localhost"
    CACHE_PREFIX: str = "cijene-me:"
    CACHE_TIME_SHORT: int = 300    # 5 minutes
    CACHE_TIME_MEDIUM: int = 1800  # 30 minutes
    CACHE_TIME_LONG: int = 3600    # 1 hour

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 