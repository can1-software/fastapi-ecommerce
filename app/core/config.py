"""Uygulama yapılandırması (ortam değişkenleri)."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Pydantic Settings ile tip güvenli config."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "ecommerce-api"
    DEBUG: bool = False
    DATABASE_URL: str = "postgresql+psycopg2://user:password@localhost:5432/ecommerce_db"


settings = Settings()
