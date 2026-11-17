from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "DUO API"
    environment: str = "development"
    api_prefix: str = "/api"
    database_url: str
    migration_database_url: str | None = None
    supabase_url: str
    supabase_publishable_key: str
    supabase_jwt_secret: str | None = None
    cors_origins: str = "https://minsk-date-ideas.vercel.app,http://localhost:3000,http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
