from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Bonnibel Notification Backend"
    database_url: str = "sqlite:///./bonnibel_notification.db"
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="BONNIBEL_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
