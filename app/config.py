"""Application configuration."""
from pydantic_settings import BaseSettings
from functools import lru_cache


def _normalize_database_url(url: str) -> str:
    """Railway and others use postgres://; SQLAlchemy+psycopg needs postgresql+psycopg://"""
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url[len("postgres://") :]
    if url.startswith("postgresql://") and "+psycopg" not in url:
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    # App
    APP_NAME: str = "Fairshare API"
    DEBUG: bool = False

    # Railway sets PORT
    PORT: int = 8000

    # Database (Railway injects DATABASE_URL from PostgreSQL service)
    DATABASE_URL: str = None
    POSTGRES_URL: str = None
    POSTGRES_DATABASE_URL: str = None
    DEFAULT_DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/fairshare"

    # Redis (Railway injects REDIS_URL from Redis service)
    REDIS_URL: str = "redis://localhost:6379/0"

    # CORS (set CORS_ORIGINS in Railway, comma-separated, e.g. https://yourapp.vercel.app)
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Auth (set SECRET_KEY in Railway env vars)
    SECRET_KEY: str = "change-me-in-production-use-secure-random-string"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    @property
    def database_url(self) -> str:
        # Try different Railway environment variable names
        url = self.DATABASE_URL or self.POSTGRES_URL or self.POSTGRES_DATABASE_URL or self.DEFAULT_DATABASE_URL
        return _normalize_database_url(url)

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
