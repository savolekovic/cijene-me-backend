from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # ... other settings
    REDIS_URL: str = "redis://localhost"
    CACHE_PREFIX: str = "cijene-me:"
    CACHE_TIME_SHORT: int = 300    # 5 minutes for frequently changing data
    CACHE_TIME_MEDIUM: int = 1800  # 30 minutes for moderately changing data
    CACHE_TIME_LONG: int = 3600    # 1 hour for rarely changing data

    class Config:
        env_file = ".env"

settings = Settings() 