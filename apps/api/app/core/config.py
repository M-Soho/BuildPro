from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str

    # Auth - Clerk
    CLERK_PEM_PUBLIC_KEY: str | None = None
    CLERK_JWKS_URL: str | None = None

    # Auth - Supabase (alternative)
    SUPABASE_URL: str | None = None
    SUPABASE_JWT_SECRET: str | None = None

    # Storage
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    AWS_S3_BUCKET: str | None = None
    AWS_S3_REGION: str = "us-east-1"
    AWS_S3_ENDPOINT_URL: str | None = None

    # Celery
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    # Security
    SECRET_KEY: str
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    # Observability
    LOG_LEVEL: str = "INFO"
    OTEL_ENABLED: bool = False
    OTEL_ENDPOINT: str | None = None

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
