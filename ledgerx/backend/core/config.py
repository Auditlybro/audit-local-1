"""Application configuration."""
from pathlib import Path
from pydantic_settings import BaseSettings

_env_path = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    """Settings from env."""

    # PostgreSQL
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ledgerx"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # JWT
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Google OAuth
    google_client_id: str = ""

    # SMTP for OTP emails
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_pass: str = ""

    # App
    app_name: str = "LedgerX API"

    class Config:
        env_file = str(_env_path)
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
