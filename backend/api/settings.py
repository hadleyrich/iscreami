"""Application settings with Pydantic v2."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(env_file=".env")

    database_url: str = Field(
        default="postgresql+psycopg://localhost:5432/iscreami",
        description="PostgreSQL database connection URL",
    )
    cors_origins: str = Field(
        default="*",
        description="Comma-separated list of allowed CORS origins",
    )
    serving_size_g: float = Field(
        default=66.0,
        description="Default serving size in grams",
    )


settings = Settings()
