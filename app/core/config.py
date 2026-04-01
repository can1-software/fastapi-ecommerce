from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "ecommerce-api"
    APP_ENV: str = "development"
    DEBUG: bool = False
    SEED_ALLOW: bool = False
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/ecommerce_db"

    JWT_SECRET_KEY: str = "change-me-use-openssl-rand-hex-32-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    MEDIA_ROOT: str = "uploads"
    MEDIA_URL_PATH: str = "/media"
    MAX_UPLOAD_BYTES: int = 5 * 1024 * 1024


settings = Settings()
