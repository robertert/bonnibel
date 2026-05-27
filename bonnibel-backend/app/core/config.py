from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

	database_url: str = "sqlite:///./bonnibel.db"
	cors_origins: list[str] = Field(
		default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173"]
	)


@lru_cache
def get_settings() -> Settings:
	return Settings()


settings = get_settings()

