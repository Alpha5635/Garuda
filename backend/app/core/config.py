"""Application configuration settings for LabelSetu."""

from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PROJECT_NAME: str = "LabelSetu Compliance Intelligence"
    API_V1_STR: str = "/api/v1"

    # PostgreSQL + PostGIS Connection
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "labelsetu_admin"
    POSTGRES_PASSWORD: str = "labelsetu_secure_pass_2026"
    POSTGRES_DB: str = "labelsetu"
    DATABASE_URL: Optional[str] = None

    # MinIO / S3 Object Storage Settings
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ROOT_USER: str = "minioadmin"
    MINIO_ROOT_PASSWORD: str = "minioadmin_secret_2026"
    MINIO_USE_SSL: bool = False
    MINIO_BUCKET_EVIDENCE: str = "labelsetu-evidence"
    MINIO_BUCKET_REPORTS: str = "labelsetu-reports"
    MINIO_BUCKET_SNAPSHOTS: str = "labelsetu-snapshots"

    # Redis Settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_URL: Optional[str] = None

    # Security and Cryptographic Audit Chain Settings
    SECRET_KEY: str = "labelsetu_secret_key_sih_2026_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    AUDIT_SALT: str = "labelsetu_audit_salt_2026"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    def get_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


settings = Settings()
