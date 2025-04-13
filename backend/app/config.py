"""
Configuration settings for the backend application.
Loads settings from environment variables with sensible defaults.
"""
import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field, validator

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application settings
    ENV: str = Field(default="development", env="ENV")
    DEBUG: bool = Field(default=True, env="DEBUG")
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")

    # CORS settings
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:5173", "http://localhost:8000"],
        env="CORS_ORIGINS"
    )

    # Session settings
    SECRET_KEY: str = Field(default="supersecretkey", env="SECRET_KEY")
    SESSION_EXPIRY_HOURS: int = Field(default=24, env="SESSION_EXPIRY_HOURS")

    # Keygen settings
    KEYGEN_ACCOUNT_ID: str = Field(default="", env="KEYGEN_ACCOUNT_ID")

    # Splitter service settings
    SPLITTER_URL: str = Field(default="http://localhost:9000", env="SPLITTER_URL")

    # MinIO settings
    MINIO_ENDPOINT: str = Field(default="localhost:9000", env="MINIO_ENDPOINT")
    MINIO_ACCESS_KEY: str = Field(default="minioadmin", env="MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY: str = Field(default="minioadmin", env="MINIO_SECRET_KEY")
    MINIO_BUCKET_NAME: str = Field(default="stems", env="MINIO_BUCKET_NAME")
    MINIO_SECURE: bool = Field(default=False, env="MINIO_SECURE")

    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS from string to list if needed."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create settings instance
settings = Settings()

# Print important settings at module load time for debugging
if settings.DEBUG:
    print(f"ENV: {settings.ENV}")
    print(f"CORS_ORIGINS: {settings.CORS_ORIGINS}")
    print(f"SPLITTER_URL: {settings.SPLITTER_URL}")
    print(f"MINIO_ENDPOINT: {settings.MINIO_ENDPOINT}")