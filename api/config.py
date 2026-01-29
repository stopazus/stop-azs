"""Configuration management for the SAR submission API."""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""
    
    # Database
    DATABASE_URL: str = "postgresql://sar_api:dev_password@localhost:5432/sar_records"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    
    # Auth
    JWT_SECRET_KEY: str = "dev_secret_change_in_production"
    JWT_ALGORITHM: str = "HS256"
    JWT_REQUIRED_SCOPE: str = "sar:write"
    
    # Security
    ALLOWED_IPS: Optional[str] = None  # Comma-separated
    RATE_LIMIT: str = "100/minute"
    
    # Redis (for rate limiting)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Observability
    LOG_LEVEL: str = "INFO"
    
    # Application
    APP_NAME: str = "SAR Submission API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


# Global settings instance
settings = Settings()
