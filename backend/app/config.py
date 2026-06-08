from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


def read_secret(value: str | None, file_path: str | None) -> str | None:
    if file_path and Path(file_path).exists():
        return Path(file_path).read_text(encoding="utf-8").strip()
    return value


class Settings(BaseSettings):
    app_name: str = "RoomPulse Store"
    app_env: str = "demo"
    api_secret_key: str | None = None
    api_secret_key_file: str | None = None
    postgres_db: str = "roompulse_store"
    postgres_user: str = "roompulse"
    postgres_password: str | None = None
    postgres_password_file: str | None = None
    database_url: str | None = None
    shop_currency: str = "EUR"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def secret_key(self) -> str:
        return read_secret(self.api_secret_key, self.api_secret_key_file) or "dev-secret"

    @property
    def db_password(self) -> str:
        return read_secret(self.postgres_password, self.postgres_password_file) or "roompulse_password"

    @property
    def resolved_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        return f"postgresql+psycopg://{self.postgres_user}:{self.db_password}@db:5432/{self.postgres_db}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
