"""Application configuration management using Pydantic Settings."""

from functools import lru_cache
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "Lexora AI"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/lexora"
    )
    database_pool_size: int = 20
    database_max_overflow: int = 10
    database_echo: bool = False

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0")

    # JWT Authentication
    secret_key: str = Field(default="change-me-in-production-min-32-characters")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # OpenAI
    openai_api_key: str = Field(default="")
    openai_model: str = "gpt-4-turbo-preview"
    openai_embedding_model: str = "text-embedding-3-small"
    openai_embedding_dimensions: int = 1536
    openai_max_tokens: int = 2000
    openai_temperature: float = 0.7

    # Document Storage
    upload_dir: str = "./uploads"
    max_file_size: int = 52428800  # 50MB
    allowed_extensions: List[str] = ["pdf", "txt", "md", "docx"]

    # Vector Storage
    faiss_index_path: str = "./data/faiss"
    embedding_batch_size: int = 100

    # Celery
    celery_broker_url: str = Field(default="redis://localhost:6379/1")
    celery_result_backend: str = Field(default="redis://localhost:6379/2")

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    sentry_dsn: Optional[str] = None

    # Rate Limiting
    rate_limit_per_minute: int = 60

    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"

    @property
    def database_sync_url(self) -> str:
        """Get synchronous database URL for Alembic migrations."""
        return self.database_url.replace("+asyncpg", "")


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
