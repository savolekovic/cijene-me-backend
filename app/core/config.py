from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # ... other settings
    REDIS_URL: str = "redis://localhost"
    CACHE_PREFIX: str = "cijene-me:"
    CACHE_TIMEOUT_SECONDS: int = 3600  # 1 hour default

    class Config:
        env_file = ".env"

settings = Settings() 