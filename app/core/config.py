from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "ecommerce-api"
    DEBUG: bool = False
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/ecommerce_db"

    JWT_SECRET_KEY: str = "change-me-use-openssl-rand-hex-32-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


settings = Settings()
