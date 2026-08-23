import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "LabelSetu Backend"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "super-secret-key-change-in-production-2026"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # JWT Settings
    JWT_SECRET_KEY: str = "jwt-super-secret-key-sih-2026-labelsetu"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database Settings
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "garuda_user"
    POSTGRES_PASSWORD: str = "garuda_secure_password"
    POSTGRES_DB: str = "labelsetu_db"
    DATABASE_URL: Optional[str] = None
    SYNC_DATABASE_URL: Optional[str] = None

    # Redis & Celery
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # S3 / MinIO Settings
    S3_ENDPOINT_URL: Optional[str] = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET_NAME: str = "labelsetu-evidence"
    S3_REGION: str = "us-east-1"
    S3_SECURE: bool = False

    # Image Quality Thresholds
    BLUR_THRESHOLD: float = 100.0
    GLARE_THRESHOLD: float = 0.15
    MIN_IMAGE_WIDTH: int = 400
    MIN_IMAGE_HEIGHT: int = 400

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def get_database_url(self) -> str:
        if self.DATABASE_URL:
            url = self.DATABASE_URL
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql+asyncpg://", 1)
            elif url.startswith("postgresql://") and "+asyncpg" not in url:
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            return url
        return "sqlite+aiosqlite:///./labelsetu.db"

    def get_sync_database_url(self) -> str:
        if self.SYNC_DATABASE_URL:
            url = self.SYNC_DATABASE_URL
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql+psycopg2://", 1)
            elif url.startswith("postgresql://") and "+psycopg2" not in url:
                return url.replace("postgresql://", "postgresql+psycopg2://", 1)
            return url
        if self.DATABASE_URL:
            url = self.DATABASE_URL
            if url.startswith("postgres://"):
                return url.replace("postgres://", "postgresql+psycopg2://", 1)
            elif url.startswith("postgresql://") and "+psycopg2" not in url:
                return url.replace("postgresql://", "postgresql+psycopg2://", 1)
            elif "+asyncpg" in url:
                return url.replace("+asyncpg", "+psycopg2")
            return url
        return "sqlite:///./labelsetu.db"


settings = Settings()
